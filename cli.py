#!/usr/bin/env python3

import time
import os
import sys
import subprocess
from pathlib import Path

ENGINE_PATH = Path(__file__).parent / "engine"
sys.path.insert(0, str(ENGINE_PATH))

import config
import database
import ui
from inventory.network import detect
import console

VERSION = "0.4.0"

VERSION_FILE = "/etc/netmonitor/version"
BUILD_FILE = "/etc/netmonitor/build"


def banner():

    print()
    print("==========================================")
    print(f"         NetMonitor v{VERSION}")
    print("==========================================")
    print()


def help_menu():

    banner()

    print("Available Commands")
    print()
    print("  init")
    print("  status")
    print("  watch")
    print("  events")
    print("  health")
    print("  service")
    print("  version")
    print("  reset")
    print()
    print("Device Commands")
    print()
    print("  device add")
    print("  device edit")
    print("  device list")
    print("  device remove")
    print()

def device_add():

    while True:

        ui.title("Add Device")

        name = input("Device Name (0=Cancel): ").strip()

        if name == "0":
            return False

        ip = input("IP Address (0=Cancel): ").strip()

        if ip == "0":
            return False

        print()

        ping = input("Enable Ping monitoring? (Y/N): ").lower().startswith("y")
        snmp = input("Enable SNMP monitoring? (Y/N): ").lower().startswith("y")

        try:

            config.add_device(
                name=name,
                ip=ip,
                ping=ping,
                snmp=snmp
            )

            subprocess.run(
                ["systemctl", "restart", "netmonitor"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            print()
            print(f'✓ Device "{name}" added successfully.')
            print()

            return True

        except Exception as e:

            print()
            print(f"ERROR: {e}")
            print()

            input("Press ENTER to try again...")

def device_list():

    ui.title("Devices")

    devices = config.get_devices()

    if not devices:

        print("No monitored devices configured.")
        print()
        return

    print(f"{'ID':<4} {'NAME':<25} {'IP ADDRESS'}")
    print("-" * 55)

    for device in devices:

        print(
            f"{device['id']:<4}"
            f"{device['name']:<25}"
            f"{device['ip']}"
        )

    print()

def device_remove():

    banner()

    devices = config.get_devices()

    if not devices:

        print("No monitored devices configured.")
        print()
        return

    print(f"{'ID':<4} {'NAME':<25} {'IP ADDRESS'}")
    print("-" * 55)

    for device in devices:

        print(
            f"{device['id']:<4}"
            f"{device['name']:<25}"
            f"{device['ip']}"
        )

    print()

    device_id = int(input("Enter device ID to remove: "))

    selected = None

    for device in devices:

        if device["id"] == device_id:
            selected = device
            break

    if selected is None:

        print()
        print("Device not found.")
        print()
        return

    print()

    answer = input(
        f'Remove "{selected["name"]}" ({selected["ip"]})? (Y/N): '
    ).strip().lower()

    if not answer.startswith("y"):

        print()
        print("Cancelled.")
        print()
        return

    config.remove_device(device_id)

    database.remove_status(selected["name"])

    subprocess.run(
        ["systemctl", "restart", "netmonitor"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print()
    print("Device removed successfully.")
    print()

def device_edit():

    banner()

    devices = config.get_devices()

    if not devices:

        print("No monitored devices configured.")
        print()
        return

    print(f"{'ID':<4} {'NAME':<25} {'IP ADDRESS'}")
    print("-" * 55)

    for device in devices:

        print(
            f"{device['id']:<4}"
            f"{device['name']:<25}"
            f"{device['ip']}"
        )

    print()

    device_id = int(input("Enter device ID : "))

    selected = None

    for device in devices:

        if device["id"] == device_id:
            selected = device
            break

    if selected is None:

        print()
        print("Device not found.")
        print()
        return

    print()

    name = input(
        f'Device Name [{selected["name"]}] : '
    ).strip()

    if name == "":
        name = selected["name"]

    ip = input(
        f'IP Address  [{selected["ip"]}] : '
    ).strip()

    if ip == "":
        ip = selected["ip"]

    ping_default = "Y" if selected["checks"]["ping"] else "N"
    snmp_default = "Y" if selected["checks"]["snmp"] else "N"

    ping = input(
        f"Enable Ping (Y/N) [{ping_default}] : "
    ).strip()

    if ping == "":
        ping = ping_default

    snmp = input(
        f"Enable SNMP (Y/N) [{snmp_default}] : "
    ).strip()

    if snmp == "":
        snmp = snmp_default

    print()

    answer = input("Save changes? (Y/N): ").strip().lower()

    if not answer.startswith("y"):

        print()
        print("Cancelled.")
        print()
        return

    config.update_device(
        device_id,
        name,
        ip,
        ping.upper().startswith("Y"),
        snmp.upper().startswith("Y")
    )

    subprocess.run(
        ["systemctl", "restart", "netmonitor"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print()
    print("Device updated successfully.")
    print()

def status():

    ui.title("Dashboard")

    customer = config.load_customer()

    print("Customer")
    print("--------")
    print(f"Customer : {customer.get('customer','Unknown')}")
    print(f"Site     : {customer.get('site','Unknown')}")
    print()

    service = subprocess.run(
        ["systemctl","is-active","netmonitor"],
        capture_output=True,
        text=True
    ).stdout.strip()

    print("Service")
    print("-------")
    print(f"Status   : {service}")
    print()

    print("Current Status")
    print("--------------")

    rows = database.get_current_status()

    print(f"{'NAME':<20} {'TYPE':<10} {'STATE':<8} LAST CHANGE")
    print("-" * 65)

    for row in rows:

        print(
            f"{row['job_name']:<20}"
            f"{row['job_type']:<10}"
            f"{row['state']:<8}"
            f"{row['last_change']}"
        )

    print()


def events():

    banner()

    rows = database.get_recent_events()

    print(f"{'DATE & TIME':<20} {'OBJECT':<20} {'STATE':<8} MESSAGE")
    print("-" * 110)

    for row in rows:

        print(
            f"{row['timestamp']:<20}"
            f"{row['job_name']:<20}"
            f"{row['state']:<8}"
            f"{row['message']}"
        )

    print()


def version():

    banner()

    version = Path(VERSION_FILE).read_text().strip()
    build = Path(BUILD_FILE).read_text().strip()

    service = subprocess.run(
        ["systemctl","is-active","netmonitor"],
        capture_output=True,
        text=True
    ).stdout.strip()

    print(f"Version : {version}")
    print(f"Build   : {build}")
    print(f"Engine  : {service}")
    print()


def service():

    banner()

    active = subprocess.run(
        ["systemctl","is-active","netmonitor"],
        capture_output=True,
        text=True
    ).stdout.strip()

    enabled = subprocess.run(
        ["systemctl","is-enabled","netmonitor"],
        capture_output=True,
        text=True
    ).stdout.strip()

    pid = subprocess.run(
        ["systemctl","show","-p","MainPID","--value","netmonitor"],
        capture_output=True,
        text=True
    ).stdout.strip()

    uptime = subprocess.run(
        ["systemctl","show","-p","ActiveEnterTimestamp","--value","netmonitor"],
        capture_output=True,
        text=True
    ).stdout.strip()

    print("NetMonitor Service")
    print("------------------")
    print(f"Status  : {active}")
    print(f"Enabled : {enabled}")
    print(f"PID     : {pid}")
    print(f"Started : {uptime}")
    print()

def init():

    banner()

    info = detect()

    print("Customer Setup")
    print("--------------")

    customer = input("Customer Name : ").strip()
    site = input("Site Name     : ").strip()

    print()
    print("Detected Network")
    print("----------------")
    print(f"Interface : {info['interface']}")
    print(f"IP        : {info['ip']}")
    print(f"Prefix    : /{info['prefix']}")
    print(f"Gateway   : {info['gateway']}")
    print(f"DNS 1     : {info['dns'][0]}")
    print(f"DNS 2     : {info['dns'][1]}")
    print()

    answer = input("Use these settings? (Y/N): ").lower()

    if not answer.startswith("y"):

        print()
        print("Cancelled.")
        print()
        return

    config.save_customer(
        {
            "version": VERSION,
            "customer": customer,
            "site": site,
            "network":
            {
                "interface": info["interface"],
                "ip": info["ip"],
                "prefix": info["prefix"],
                "gateway": info["gateway"],
                "dns": info["dns"]
            },
            "tailscale": True
        }
    )

    database.initialize()

    subprocess.run(
        ["systemctl", "restart", "netmonitor"],
        check=True
    )

    print()
    print("Initialization complete.")
    print()

def reset():

    banner()

    answer = input(
        "This will erase the current NetMonitor configuration.\nContinue? (Y/N): "
    ).strip().lower()

    if not answer.startswith("y"):

        print()
        print("Cancelled.")
        print()
        return

    subprocess.run(["systemctl", "stop", "netmonitor"])

    files = [
        "/etc/netmonitor/netmonitor.json",
        "/etc/netmonitor/devices.json",
        "/var/lib/netmonitor/netmonitor.db"
    ]

    for filename in files:

        try:
            Path(filename).unlink()
        except FileNotFoundError:
            pass

    config.save_customer(
        {
            "version": VERSION,
            "customer": "",
            "site": "",
            "network": {},
            "tailscale": True
        }
    )

    config.save_devices(
        {
            "devices": []
        }
    )

    database.initialize()

    subprocess.run(["systemctl", "start", "netmonitor"])

    print()
    print("Reset complete.")
    print()
    print("Run:")
    print()
    print("    sudo nm init")
    print()

def watch():

    try:

        while True:

            os.system("clear")

            status()

            time.sleep(2)

    except KeyboardInterrupt:

        print()
        print("Stopping watch mode.")
        print()

def main():

    args = sys.argv[1:]

    if not args:
        console.run()
        return

    if args[0] == "init":
        init()
        return

    if args[0] == "reset":
        reset()
        return

    if args[0] == "watch":
        watch()
        return

    if args[0] == "status":
        status()
        return

    if args[0] == "events":
        events()
        return

    if args[0] == "version":
        version()
        return

    if args[0] == "service":
        service()
        return

    if args[0] == "device":

        if len(args) < 2:
            print("Usage: nm device add|list|remove")
            return

        if args[1] == "add":
            device_add()
            return

        if args[1] == "edit":
            device_edit()
            return

        if args[1] == "list":
            device_list()
            return

        if args[1] == "remove":
            device_remove()
            return

    print("Command not implemented yet.")


if __name__ == "__main__":
    main()
