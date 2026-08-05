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
from engine import analyzer
from inventory.network import detect

VERSION = "0.4.0"

VERSION_FILE = "/etc/netmonitor/version"
BUILD_FILE = "/etc/netmonitor/build"

def banner():
    ui.banner()

def help_menu():

    os.system("clear")

    while True:

        os.system("clear")

        banner()

        print("Main Menu")
        print("---------")
        print()
        print("1) Initialize")
        print("2) Status")
        print("3) Live Watch")
        print("4) Events")
        print("5) Incidents")
        print("6) Scout Analysis")
        print()
        print("7) Devices")
        print("8) Configuration")
        print("9) Service")
        print("V) Version")
        print("R) Reset")
        print()
        print("Q) Quit")
        print()

        choice = input("Selection: ").strip().lower()

        if choice == "1":
            os.system("clear")
            subprocess.run(["nm", "init"])

        elif choice == "2":
            os.system("clear")
            status()

        elif choice == "3":
            watch()
            continue

        elif choice == "4":
            os.system("clear")
            events()

        elif choice == "5":
            os.system("clear")
            incidents()

        elif choice == "6":
            os.system("clear")
            scout_analysis()

        elif choice == "7":
            os.system("clear")
            device_menu()
            continue

        elif choice == "8":
            os.system("clear")
            configuration_menu()
            continue

        elif choice == "9":
            os.system("clear")
            service()

        elif choice == "v":
            os.system("clear")
            version()
            
        elif choice == "r":
            os.system("clear")
            subprocess.run(["nm", "reset"])

        elif choice == "q":
            os.system("clear")
            return

        input("\nPress Enter to continue...")

def configuration_menu():

    os.system("clear")

    while True:

        banner()

        print("Configuration")
        print("-------------")
        print()
        print("1) Customer Name")
        print("2) Site Name")
        print("3) Router Name")
        print()
        print("B) Back")
        print()

        choice = input("Selection: ").strip().lower()

        if choice == "1":

            print()
            print("Coming soon.")

        elif choice == "2":

            print()
            print("Coming soon.")

        elif choice == "3":

            print()
            print("Coming soon.")
            
        elif choice == "b":

            os.system("clear")
            return

        else:

            print()
            print("Invalid selection.")

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
        print("4) Edit Device")
        print("5) Remove Device")
        print()
        print("B) Back")
        print()

        choice = input("Selection: ").strip().lower()

        if choice == "1":
            os.system("clear")
            device_list()

        elif choice == "2":
            os.system("clear")
            subprocess.run(["nm", "device", "scan"])

        elif choice == "3":
            os.system("clear")
            subprocess.run(["nm", "device", "add"])

        elif choice == "4":
            os.system("clear")
            subprocess.run(["nm", "device", "edit"])

        elif choice == "5":
            os.system("clear")
            subprocess.run(["nm", "device", "remove"])

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
        ui.error(str(e))
        print()
        return

    print()
    ui.success("Device added successfully.")

    ui.info("Restarting NetMonitor...")

    subprocess.run(
        ["systemctl", "restart", "netmonitor"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    ui.success("Done.")
    print()

def device_list():

    banner()

    devices = config.get_devices()

    if not devices:

        ui.warning("No monitored devices configured.")
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

    while True:

        banner()

        devices = config.get_devices()

        if not devices:

            ui.warning("No monitored devices configured.")
            print()
            input("Press ENTER to continue...")
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
            ui.error("No valid devices selected.")
            print()
            input("Press ENTER to continue...")
            continue

        print()
        print("The following devices will be removed:")
        print()

        for device in selected_devices:

            print(f"  {device['name']} ({device['ip']})")

        print()

        answer = input("Proceed? (Y/N): ").strip().lower()

        if not answer.startswith("y"):

            print()
            ui.warning("Cancelled.")
            print()
            input("Press ENTER to continue...")
            return

        for selected in selected_devices:

            config.remove_device(selected["id"])
            database.remove_status(selected["name"])

            ui.success(f"✓ Removed {selected['name']}")
            removed += 1

        if removed:

            print()
            ui.info("Restarting NetMonitor...")

            subprocess.run(
                ["systemctl", "restart", "netmonitor"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            ui.success("Done.")

        print()
        ui.success(f"{removed} device(s) removed.")
        print()

        again = input(
            "Remove another device? (Y/N): "
        ).strip().lower()

        if not again.startswith("y"):

            return
            
def device_edit():

    banner()

    devices = config.get_devices()

    if not devices:

        ui.warning("No monitored devices configured.")
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
        ui.error("Device not found.")
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
        ui.warning("Cancelled.")
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
    ui.info("Scanning network...")
    print()

    devices = scanner.scan()

    if not devices:
        ui.warning("No devices found.")
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

            ui.success(f"✓ Added {name}")

            added += 1

        except Exception as e:
            ui.error(str(e))

    if added:

        print()
        ui.info("Restarting NetMonitor...")

        subprocess.run(
            ["systemctl", "restart", "netmonitor"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        ui.success("Done.")

    print()
    print(f"{added} device(s) added.")

def status():

    banner()

    customer = config.load_customer()

    gateway_name = customer["network"].get(
        "gateway_name",
        "Gateway"
    )

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

    service_state = "UP" if service.strip() == "active" else "DOWN"
    print(f"Status   : {ui.state(service_state)}")

    print()
    print("Current Status")
    print("--------------")

    rows = database.get_current_status()

    print(f"{'NAME':<25} {'TYPE':<10} {'STATE':<18} LAST CHANGE")
    print("-" * 75)

    for row in rows:

        name = row["job_name"]

        if name == "Gateway":

            name = gateway_name

        if len(name) > 25:
            name = name[:22] + "..."

        print(
            f"{name:<25}"
            f"{row['job_type']:<10}"
            f"{ui.state(row['state']):<18}"
            f"{row['last_change']}"
        )

    print()
    
def clear_events():

    banner()

    print("Clear Event History")
    print("===================")
    print()

    print("This will permanently delete:")
    print("  • All recorded events")
    print("  • All derived incidents")
    print()

    print("The following will NOT be affected:")
    print("  ✓ Customer configuration")
    print("  ✓ Site configuration")
    print("  ✓ Device configuration")
    print("  ✓ Current monitoring")
    print()

    answer = input("Type YES to continue: ")

    if answer != "YES":

        print()
        print("Operation cancelled.")
        return

    database.clear_history()

    print()
    print("Event history successfully cleared.")
    print("Scout will now begin recording a new history.")

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

    status = "UP" if active == "active" else "DOWN"
    print(f"Status  : {ui.state(status)}")
    enabled_state = "UP" if enabled == "enabled" else "DOWN"
    print(f"Enabled : {ui.state(enabled_state)}")
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
        ui.warning("Cancelled.")
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
    ui.success("Initialization complete.")
    print()

def reset():

    banner()

    answer = input(
        "This will erase the current NetMonitor configuration.\nContinue? (Y/N): "
    ).strip().lower()

    if not answer.startswith("y"):

        print()
        ui.warning("Cancelled.")
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
    ui.success("Reset complete.")
    print()
    print("Select 'Initialize' from the Main Menu")
    print("to configure Scout for a new customer.")
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

        if len(args) > 1:

            if args[1] == "clear":

                clear_events()
                return

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

def scout_analysis():

    banner()

    report = analyzer.analyze()

    print("Scout Analysis")
    print("==============")
    print()

    print("Executive Summary")
    print("-----------------")
    print()

    print(f"Overall Health : {report['health']}")
    print()

    if report["findings"]:

        first = report["findings"][0]

        print("Scout's Assessment")
        print("------------------")
        print()

        if first["type"] == "INFRASTRUCTURE":

            print(
                "Scout detected a site-wide infrastructure outage."
            )

            print()

            print(
                f"{first['count']} monitored devices became "
                "unreachable during the incident."
            )

            print(
                "The event is consistent with a failure of the "
                "gateway, core switch or site power."
            )

        elif first["type"] == "DEVICE":

            print(
                f"Scout identified {first['device']} as the "
                "least reliable monitored device."
            )

            print()

            print(
                f"{first['count']} outage/recovery cycles have "
                "been recorded."
            )

            print(
                "No evidence currently suggests a wider network "
                "problem."
            )

        print()

        print("Recommended Investigation Order")
        print("-------------------------------")
        print()

        for number, finding in enumerate(
            report["top_findings"],
            start=1
        ):

            if "device" in finding:

                print(
                    f"{number}. Inspect {finding['device']}"
                )

            else:

                print(
                    f"{number}. Investigate network infrastructure"
                )

        print()

    print("Network Statistics")
    print("------------------")
    print()

    print(f"Incidents              : {report['total_incidents']}")
    print(f"Infrastructure Outages : {report['major_outages']}")
    print(
        f"Device Incidents       : "
        f"{report['single_device'] + report['multi_device']}"
    )
    print(
        f"Devices Monitored      : "
        f"{report['devices_monitored']}"
    )

    if report["device_counter"]:

        worst, count = report["device_counter"].most_common(1)[0]

        print(
            f"Worst Device           : "
            f"{worst} ({count})"
        )

    print()

    print("Device Reliability")
    print("------------------")
    print()

    if report["device_reliability"]:

        for device in report["device_reliability"]:

            downtime = device["downtime"]

            hours = downtime // 3600
            minutes = (downtime % 3600) // 60
            seconds = downtime % 60

            if hours:

                downtime_text = (
                    f"{hours}h {minutes}m {seconds}s"
                )

            elif minutes:

                downtime_text = (
                    f"{minutes}m {seconds}s"
                )

            else:

                downtime_text = (
                    f"{seconds}s"
                )

            print(
                f"{device['device']:<20} "
                f"{device['score']:>3}%   "
                f"{device['health']}"
            )

            print(
                f"{'':20} "
                f"Outages : {device['outages']}"
            )

            print(
                f"{'':20} "
                f"Downtime: {downtime_text}"
            )

            print()

    else:

        print("No reliability data available.")

    print()
    
if __name__ == "__main__":
    main()
