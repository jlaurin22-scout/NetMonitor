#!/usr/bin/env python3

import subprocess

import ui

from engine import config


def select_network(networks):

    if len(networks) == 1:

        return networks[0]["id"]

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

        return None

    try:

        network_id = int(selection)

    except ValueError:

        raise ValueError(
            "Invalid network ID."
        )

    if not any(
        network["id"] == network_id
        for network in networks
    ):

        raise ValueError(
            "Network not found."
        )

    return network_id


def select_monitoring_mode():

    print()

    print("Monitoring Mode:")
    print()

    print("N) Normal")
    print("S) Standby")
    print("C) Conditional")

    print()

    selection = input(
        "Monitoring Mode [N]: "
    ).strip().lower()

    if selection == "":

        return "normal"

    modes = {
        "n": "normal",
        "s": "standby",
        "c": "conditional",
    }

    if selection not in modes:

        raise ValueError(
            "Invalid monitoring mode."
        )

    return modes[selection]


def get_network_name(
    networks,
    network_id
):

    for network in networks:

        if network["id"] == network_id:

            return network["name"]

    return f"Network {network_id}"


def device_add():

    ui.banner("Add Monitored Device")

    networks = config.get_networks()

    if not networks:

        ui.error(
            "No networks configured."
        )

        print()

        return True

    print()

    try:

        network_id = select_network(
            networks
        )

    except ValueError as e:

        print()

        ui.error(
            str(e)
        )

        print()

        return True

    if network_id is None:

        return False

    print()

    name = input(
        "Device Name : "
    ).strip()

    if name.lower() == "c":

        return False

    if name == "":

        ui.error(
            "Device Name cannot be empty."
        )

        print()

        return True

    ip = input(
        "IP Address  : "
    ).strip()

    if ip.lower() == "c":

        return False

    if ip == "":

        ui.error(
            "IP Address cannot be empty."
        )

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

    try:

        monitoring_mode = (
            select_monitoring_mode()
        )

    except ValueError as e:

        print()

        ui.error(
            str(e)
        )

        print()

        return True

    network_name = get_network_name(
        networks,
        network_id
    )

    print()

    print("New Device:")
    print()

    print(
        f"  Name:          {name}"
    )

    print(
        f"  IP Address:    {ip}"
    )

    print(
        f"  Network:       {network_name}"
    )

    print(
        f"  Ping:          "
        f"{'Enabled' if ping else 'Disabled'}"
    )

    print(
        f"  SNMP:          "
        f"{'Enabled' if snmp else 'Disabled'}"
    )

    print(
        f"  Monitoring:    "
        f"{monitoring_mode.upper()}"
    )

    print()

    answer = input(
        "Add device? (Y/N): "
    ).strip().lower()

    if answer != "y":

        print()

        ui.warning(
            "Cancelled."
        )

        print()

        return False

    try:

        config.add_device(
            name=name,
            ip=ip,
            ping=ping,
            snmp=snmp,
            network_id=network_id,
            monitoring_mode=monitoring_mode
        )

    except Exception as e:

        print()

        ui.error(
            str(e)
        )

        print()

        return True

    print()

    ui.success(
        "Device added successfully."
    )

    ui.info(
        "Restarting NetMonitor..."
    )

    subprocess.run(
        [
            "systemctl",
            "restart",
            "netmonitor"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    ui.success("Done.")

    print()

    return True