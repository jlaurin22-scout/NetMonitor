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
from commands.device.add import device_add
from commands.device.list import device_list
from commands.device.network import network_list
from commands.device.edit import device_edit
from commands.device.remove import device_remove
from commands.device.scan import device_scan
from commands.events import (
    clear_events,
    events,
    incidents,
)
from commands.analysis import scout_analysis
from setup.networks import run as network_setup
from setup.devices import run as device_setup
from setup.installer import run as install_appliance

ENGINE_PATH = Path(__file__).parent / "engine"
sys.path.insert(0, str(ENGINE_PATH))

import config
import database
import ui


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
        print("5) Scout Analysis")
        print()
        print("6) Devices")
        print("7) Configuration")
        print("8) Service")
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

            while True:

                os.system("clear")

                banner()

                print("Events")
                print("------")
                print()
                print("1) View Recent Events")
                print("2) View Incidents")
                print("3) Clear Event History")
                print()
                print("B) Back")
                print()

                event_choice = input(
                    "Selection: "
                ).strip().lower()

                if event_choice == "1":

                    os.system("clear")
                    events()
                    input("\nPress Enter to continue...")

                elif event_choice == "2":

                    os.system("clear")
                    incidents()
                    input("\nPress Enter to continue...")

                elif event_choice == "3":

                    os.system("clear")
                    clear_events()
                    input("\nPress Enter to continue...")

                elif event_choice == "b":

                    break

        elif choice == "5":

            os.system("clear")
            scout_analysis()

        elif choice == "6":

            os.system("clear")
            device_menu()
            continue

        elif choice == "7":

            os.system("clear")
            configuration_menu()
            continue

        elif choice == "8":

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

        if choice not in ("4", "7", "8", "q"):

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

            os.system("clear")
            edit_network_menu()
            continue

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
    gateway_name = input("Router / Firewall  : ").strip()
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


def edit_network_menu():

    ui.banner()

    networks = config.get_networks()

    if not networks:

        ui.warning("No networks configured.")
        print()
        return

    print("Edit Network")
    print("------------")
    print()

    print(
        f"{'ID':<4}"
        f"{'NAME':<20}"
        f"{'INTERFACE':<12}"
        f"{'GATEWAY':<16}"
    )

    print("-" * 65)

    for network in networks:

        print(
            f"{network['id']:<4}"
            f"{network['name']:<20}"
            f"{network['interface']:<12}"
            f"{network['gateway']:<16}"
        )

    print()
    print("B) Back")
    print()

    selection = input(
        "Enter network ID: "
    ).strip().lower()

    if selection == "b":

        return

    try:

        network_id = int(selection)

    except ValueError:

        print()
        ui.error("Invalid network ID.")
        print()
        return

    selected = None

    for network in networks:

        if network["id"] == network_id:

            selected = network
            break

    if selected is None:

        print()
        ui.error("Network not found.")
        print()
        return

    print()
    print("Edit Network")
    print("------------")
    print()

    name = input(
        f"Network Name      [{selected['name']}] : "
    ).strip()

    if name == "":

        name = selected["name"]

    interface = input(
        f"Interface         [{selected['interface']}] : "
    ).strip()

    if interface == "":

        interface = selected["interface"]

    ip = input(
        f"IP Address        [{selected['ip']}] : "
    ).strip()

    if ip == "":

        ip = selected["ip"]

    prefix_input = input(
        f"Prefix            [{selected['prefix']}] : "
    ).strip()

    if prefix_input == "":

        prefix = selected["prefix"]

    else:

        try:

            prefix = int(prefix_input)

        except ValueError:

            print()
            ui.error("Invalid prefix.")
            print()
            return

    gateway = input(
        f"Gateway           [{selected['gateway']}] : "
    ).strip()

    if gateway == "":

        gateway = selected["gateway"]

    gateway_name = input(
        f"Router / Firewall  [{selected.get('gateway_name', 'Router / Firewall')}] : "
    ).strip()

    if gateway_name == "":

        gateway_name = selected.get(
            "gateway_name",
            "Router / Firewall"
        )

    current_dns = selected.get(
        "dns",
        [
            "",
            ""
        ]
    )

    dns1_default = current_dns[0] if len(current_dns) > 0 else ""
    dns2_default = current_dns[1] if len(current_dns) > 1 else ""

    dns1 = input(
        f"Primary DNS       [{dns1_default}] : "
    ).strip()

    if dns1 == "":

        dns1 = dns1_default

    dns2 = input(
        f"Secondary DNS     [{dns2_default}] : "
    ).strip()

    if dns2 == "":

        dns2 = dns2_default

    print()
    print("Save changes? (Y/N)")
    answer = input(
        "Selection: "
    ).strip().lower()

    if not answer.startswith("y"):

        print()
        ui.warning("Cancelled.")
        print()
        return

    try:

        config.update_network(
            network_id,
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

        subprocess.run(
            ["systemctl", "restart", "netmonitor"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print()
        ui.success("Network updated successfully.")
        print()

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
            device_scan()

            os.system("clear")
            continue
            
        elif choice == "3":

            os.system("clear")
            device_add()

        elif choice == "4":

            os.system("clear")
            device_edit()

        elif choice == "5":

            os.system("clear")
            device_remove()

        elif choice == "b":

            os.system("clear")
            return

        input("\nPress Enter to continue...")
        os.system("clear")


def init():

    banner()

    customer_info = customer_setup()

    customer = customer_info["customer"]
    address = customer_info["address"]

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
            "customer": customer,
            "address": address,
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
            "customer": "",
            "address": "",
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


if __name__ == "__main__":

    main()