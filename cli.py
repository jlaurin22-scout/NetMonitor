#!/usr/bin/env python3

from setup.customer import run as customer_setup
import time
import os
import sys
import subprocess
from pathlib import Path
from commands.version import version
from commands.service import service
from commands.status import status
from commands.device import (
    device_add,
    device_edit,
    device_list,
    device_remove,
    device_scan,
)
from commands.events import (
    clear_events,
    events,
    incidents,
)
from setup.networks import run as network_setup
from setup.devices import run as device_setup
from setup.installer import run as install_appliance

ENGINE_PATH = Path(__file__).parent / "engine"
sys.path.insert(0, str(ENGINE_PATH))

# import config
# import database
import ui
from engine import analyzer
# from inventory.network import detect

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
            init()

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
            reset()

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
        print("1) Customer")
        print("2) Site")
        print("3) Networks")
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

            os.system("clear")
            networks_menu()
            continue

        elif choice == "b":

            os.system("clear")
            return

        else:

            print()
            print("Invalid selection.")

        input("\nPress Enter to continue...")
        os.system("clear")
 
def networks_menu():

    os.system("clear")

    while True:

        banner()

        print("Networks")
        print("--------")
        print()
        print("1) List Networks")
        print("2) Add Network")
        print("3) Edit Network")
        print("4) Remove Network")
        print()
        print("B) Back")
        print()

        choice = input("Selection: ").strip().lower()

        if choice == "1":

            os.system("clear")
            network_list()

        elif choice == "2":

            os.system("clear")
            add_network_menu()

        elif choice == "3":

            print()
            print("Coming in Build 0.5.0-dev2")

        elif choice == "4":

            print()
            print("Coming in Build 0.5.0-dev2")

        elif choice == "b":

            os.system("clear")
            return

        else:

            print()
            print("Invalid selection.")

        input("\nPress Enter to continue...")
        os.system("clear")

def add_network_menu():

    banner()

    print("Add Network")
    print("-----------")
    print()

    name = input("Network Name      : ").strip()
    interface = input("Interface         : ").strip()
    ip = input("IP Address        : ").strip()
    prefix = int(input("Prefix            : ").strip())
    gateway = input("Gateway           : ").strip()
    gateway_name = input("Gateway Name      : ").strip()
    dns1 = input("Primary DNS       : ").strip()
    dns2 = input("Secondary DNS     : ").strip()

    try:

        network_id = config.add_network(
            name,
            interface,
            ip,
            prefix,
            gateway,
            gateway_name,
            [
                dns1,
                dns2
            ]
        )

        print()
        ui.success(
            f"Network added successfully (ID {network_id})."
        )

    except Exception as e:

        print()
        ui.error(str(e))

    print()
        
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
   
def init():

    banner()

    customer_info = customer_setup()

    customer = customer_info["customer"]
    site = customer_info["site"]
    
    networks = network_setup()

    if networks is None:

        return

    if len(networks) == 0:

        print()
        ui.warning("Initialization cancelled.")
        print()

        return

    config.save_customer(
        {
            "version": VERSION,
            "customer": customer,
            "site": site,
            "networks": networks,
            "tailscale": True
        }
    )

    device_setup(networks)

    install_appliance()

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
            "networks": [],
            "tailscale": True
        }
    )

    config.save_devices(
        {
            "devices": []
        }
    )

    database.initialize()

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
