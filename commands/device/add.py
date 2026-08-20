#!/usr/bin/env python3

import subprocess

import ui

from engine import config

from .common import add_monitored_device


def device_add():

    ui.banner("Add Monitored Device")

    networks = config.get_networks()

    if not networks:

        ui.error("No networks configured.")
        print()
        return True

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
    print("C) Cancel")
    print()

    selection = input(
        "Enter network ID: "
    ).strip().lower()

    if selection == "c":

        return False

    try:

        network_id = int(selection)

    except ValueError:

        print()
        ui.error("Invalid network ID.")
        print()
        return True

    if not any(
        network["id"] == network_id
        for network in networks
    ):

        print()
        ui.error("Network not found.")
        print()
        return True

    print()

    name = input("Device Name : ").strip()

    if name.lower() == "c":

        return False

    if name == "":

        ui.error("Device Name cannot be empty.")
        print()
        return True

    ip = input("IP Address  : ").strip()

    if ip.lower() == "c":

        return False

    if ip == "":

        ui.error("IP Address cannot be empty.")
        print()
        return True

    print()

    ping_input = input(
        "Enable Ping monitoring? (Y/N): "
    ).strip().lower()

    if ping_input == "c":

        return False

    ping = ping_input.startswith("y")

    snmp_input = input(
        "Enable SNMP monitoring? (Y/N): "
    ).strip().lower()

    if snmp_input == "c":

        return False

    snmp = snmp_input.startswith("y")

    print()

    answer = input(
        "Add device? (Y/N): "
    ).strip().lower()

    if answer != "y":

        print()
        ui.warning("Cancelled.")
        print()
        return False

    try:

        add_monitored_device(
            name,
            ip,
            ping,
            snmp,
            network_id
        )

    except Exception as e:

        print()
        ui.error(str(e))
        print()
        return True

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

    input("Press ENTER to continue...")

    return True
