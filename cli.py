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
from inventory.network import detect

VERSION = "0.4.0"

VERSION_FILE = "/etc/netmonitor/version"
BUILD_FILE = "/etc/netmonitor/build"

def banner():

    print(rf"""
 ███████╗ ██████╗ ██████╗ ██╗   ██╗████████╗
 ██╔════╝██╔════╝██╔═══██╗██║   ██║╚══██╔══╝
 ███████╗██║     ██║   ██║██║   ██║   ██║
 ╚════██║██║     ██║   ██║██║   ██║   ██║
 ███████║╚██████╗╚██████╔╝╚██████╔╝   ██║
 ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝

                 Scout Console
                 Version {VERSION}

""")

def help_menu():

    os.system("clear")

    while True:

        os.system("clear")

        banner()

        print("Main Menu")
        print("---------")
        print()
        print("1) Status")
        print("2) Live Watch")
        print("3) Events")
        print("4) Incidents")
        print()
        print("5) Devices")
        print("6) Service")
        print("7) Version")
        print("8) Reset")
        print()
        print("Q) Quit")
        print()

        choice = input("Selection: ").strip().lower()

        if choice == "1":
            os.system("clear")
            status()

        elif choice == "2":
            watch()
            continue

        elif choice == "3":
            os.system("clear")
            events()

        elif choice == "4":
            os.system("clear")
            incidents()

        elif choice == "5":
            os.system("clear")
            device_menu()
            continue

        elif choice == "6":
            os.system("clear")
            service()

        elif choice == "7":
            os.system("clear")
            version()

        elif choice == "8":
            os.system("clear")
            reset()

        elif choice == "q":
            os.system("clear")
            return

        input("\nPress Enter to continue...")
        os.system("clear")

def device_menu():

    os.system("clear")

    while True:

        banner()

        print("Devices")
        print("-------")
        print()
        print("1) List Devices")
        print("2) Scan Network & Add")
        print("3) Add Device Manually")
        print("4) Remove Device")
        print()
        print("B) Back")
        print()

        choice = input("Selection: ").strip().lower()

        if choice == "1":
            os.system("clear")
            device_list()

        elif choice == "2":
            os.system("clear")
            device_scan()

        elif choice == "3":
            os.system("clear")
            device_add()

        elif choice == "4":
            os.system("clear")
            device_remove()

        elif choice == "b":
            os.system("clear")
            return

        input("\nPress Enter to continue...")
        os.system("clear")

def add_monitored_device(name, ip, ping=True, snmp=False):

    config.add_device(
        name=name,
        ip=ip,
        ping=ping,
        snmp=snmp
    )

def device_add():

    banner()

    print("Add Monitored Device")
    print("--------------------")

    name = input("Device Name : ").strip()
    ip = input("IP Address  : ").strip()

    print()

    ping = input("Enable Ping monitoring? (Y/N): ").lower().startswith("y")
    snmp = input("Enable SNMP monitoring? (Y/N): ").lower().startswith("y")

    try:
        add_monitored_device(name, ip, ping, snmp)

    except Exception as e:

        print()
        print(f"ERROR: {e}")
        print()
        return

    print()
    print("Device added successfully.")

    print("Restarting NetMonitor...")

    subprocess.run(
        ["systemctl", "restart", "netmonitor"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("Done.")
    print()

def device_list():

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

    selection = input(
        "Enter device ID(s) to remove (e.g. 2,5,8): "
    ).strip()

    if not selection:
        return  

    removed = 0

    selected_devices = []

    for item in selection.split(","):

        try:
            device_id = int(item.strip())

        except ValueError:
            continue

        for device in devices:

            if device["id"] == device_id:
                selected_devices.append(device)
                break

    if not selected_devices:

        print()
        print("No valid devices selected.")
        print()
        return

    print()
    print("The following devices will be removed:")
    print()

    for device in selected_devices:

        print(f"  {device['name']} ({device['ip']})")

    print()

    answer = input("Proceed? (Y/N): ").strip().lower()

    if not answer.startswith("y"):

        print()
        print("Cancelled.")
        print()
        return

    for selected in selected_devices:

        config.remove_device(selected["id"])
        database.remove_status(selected["name"])

        print(f"✓ Removed {selected['name']}")
        removed += 1

    if removed:

        print()
        print("Restarting NetMonitor...")

        subprocess.run(
            ["systemctl", "restart", "netmonitor"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print("Done.")

    print()
    print(f"{removed} device(s) removed.")

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

def device_scan():

    from engine.inventory import scanner

    print()
    print("Scanning network...")
    print()

    devices = scanner.scan()

    if not devices:
        print("No devices found.")
        return

    print(
        f"{'#':>2} "
        f"{'IP Address':15} "
        f"{'Hostname':22} "
        f"{'Type':18} "
        f"{'SNMP':5}"
    )

    print("-" * 70)

    for i, device in enumerate(devices, 1):

        snmp = "Yes" if device.snmp else "No"

        print(
            f"{i:>2} "
            f"{device.ip:15} "
            f"{device.hostname[:22]:22} "
            f"{device.device_type[:18]:18} "
            f"{snmp:5}"
        )
    print()

    selection = input(
        "Select device(s) to add (e.g. 1,3,5 or Enter to cancel): "
    ).strip()

    if not selection:
        return

    added = 0

    for item in selection.split(","):

        try:
            index = int(item.strip()) - 1

            if index < 0 or index >= len(devices):
                continue

            device = devices[index]

            name = device.hostname.strip()

            if not name or name.lower() == "unknown":
                name = device.ip

            add_monitored_device(
                name=name,
                ip=device.ip,
                ping=True,
                snmp=device.snmp
            )

            print(f"✓ Added {name}")

            added += 1

        except Exception as e:
            print(f"✗ {e}")

    if added:

        print()
        print("Restarting NetMonitor...")

        subprocess.run(
            ["systemctl", "restart", "netmonitor"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print("Done.")

    print()
    print(f"{added} device(s) added.")

def status():

    banner()

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

    print(f"{'DATE & TIME':<20} {'STATE':<6} {'OBJECT':<24} MESSAGE")
    print("-" * 90)

    for row in rows:

        print(
            f"{row['timestamp']:<20}"
            f"{row['state']:<6}"
            f"{row['job_name']:<24}"
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

    print()
    print("Starting Live Watch...")
    print()
    print("Press Ctrl+C at any time to return to the Main Menu.")
    print()
    input("Press Enter to begin...")
    
    try:

        while True:

            os.system("clear")

            status()

            time.sleep(2)

    except KeyboardInterrupt:

        print()
        print("Returning to Main Menu...")
        time.sleep(1)

def main():

    args = sys.argv[1:]

    if not args:
        help_menu()
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

    if args[0] == "incidents":
        incidents()
        return

    if args[0] == "version":
        version()
        return

    if args[0] == "service":
        service()
        return

    if args[0] == "device":

        if len(args) < 2:
            print("Usage: nm device scan|add|list|remove")
            return

        if args[1] == "scan":
            device_scan()
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

def incidents():

    from datetime import datetime

    banner()

    incidents = database.get_incidents()

    if not incidents:
        print("No incidents found.\n")
        return

    for i, incident in enumerate(reversed(incidents), 1):

        start = datetime.strptime(
            incident["start"], "%Y-%m-%d %H:%M:%S"
        )
        end = datetime.strptime(
            incident["end"], "%Y-%m-%d %H:%M:%S"
        )

        duration = end - start

        print(f"Incident {i}")
        print("-" * 60)
        print(f"Started : {incident['start']}")
        print(f"Ended   : {incident['end']}")
        print(f"Duration: {duration}")
        print("Affected:")

        for obj in sorted(incident["objects"]):
            print(f"  {obj}")

        print()

if __name__ == "__main__":
    main()
