#!/usr/bin/env python3

import subprocess

import ui

from engine import config


def select_network(
    networks,
    current_network_id
):

    print()

    print("Networks:")
    print()

    for network in networks:

        marker = (
            "*"
            if network["id"] == current_network_id
            else " "
        )

        print(
            f"{marker} "
            f"{network['id']}) "
            f"{network['name']} "
            f"({network['interface']})"
        )

    print()
    print("Press ENTER to keep the current network.")
    print()

    selection = input(
        f"Network ID [{current_network_id}] : "
    ).strip()

    if selection == "":

        return current_network_id

    try:

        network_id = int(selection)

    except ValueError:

        raise ValueError(
            "Invalid network ID."
        )

    for network in networks:

        if network["id"] == network_id:

            return network_id

    raise ValueError(
        "Network not found."
    )


def select_monitoring_mode(
    current_mode
):

    print()

    print("Monitoring Mode:")
    print()

    print(
        "N) Normal"
        +
        (
            "  [current]"
            if current_mode == "normal"
            else ""
        )
    )

    print(
        "S) Standby"
        +
        (
            "  [current]"
            if current_mode == "standby"
            else ""
        )
    )

    print(
        "C) Conditional"
        +
        (
            "  [current]"
            if current_mode == "conditional"
            else ""
        )
    )

    print()
    print(
        "Press ENTER to keep the current mode."
    )
    print()

    selection = input(
        f"Monitoring Mode [{current_mode}] : "
    ).strip().lower()

    if selection == "":

        return current_mode

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


def device_edit():

    ui.banner("Edit Device")

    devices = config.get_devices()

    if not devices:

        ui.warning(
            "No monitored devices configured."
        )

        print()

        input(
            "Press ENTER to continue..."
        )

        return

    print(
        f"{'ID':<4}"
        f"{'NAME':<25}"
        f"{'IP ADDRESS'}"
    )

    print("-" * 55)

    for device in devices:

        print(
            f"{device['id']:<4}"
            f"{device['name']:<25}"
            f"{device['ip']}"
        )

    print()
    print("C) Cancel")
    print()

    device_selection = input(
        "Enter device ID : "
    ).strip().lower()

    if device_selection == "c":

        return

    try:

        device_id = int(
            device_selection
        )

    except ValueError:

        print()

        ui.error(
            "Invalid device ID."
        )

        print()

        return

    selected = None

    for device in devices:

        if device["id"] == device_id:

            selected = device

            break

    if selected is None:

        print()

        ui.error(
            "Device not found."
        )

        print()

        return

    networks = config.get_networks()

    current_network_id = selected.get(
        "network_id"
    )

    if current_network_id is None:

        if len(networks) == 1:

            current_network_id = (
                networks[0]["id"]
            )

        else:

            current_network_id = 1

    current_mode = (
        config.get_device_monitoring_mode(
            selected
        )
    )

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

    try:

        network_id = select_network(
            networks,
            current_network_id
        )

    except ValueError as e:

        print()

        ui.error(
            str(e)
        )

        print()

        return

    ping_default = (
        "Y"
        if selected["checks"]["ping"]
        else "N"
    )

    snmp_default = (
        "Y"
        if selected["checks"]["snmp"]
        else "N"
    )

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

    try:

        monitoring_mode = (
            select_monitoring_mode(
                current_mode
            )
        )

    except ValueError as e:

        print()

        ui.error(
            str(e)
        )

        print()

        return

    print()

    print("Changes:")
    print()

    print(
        f"  Name:          {name}"
    )

    print(
        f"  IP Address:    {ip}"
    )

    selected_network = None

    for network in networks:

        if network["id"] == network_id:

            selected_network = network

            break

    if selected_network:

        print(
            f"  Network:       "
            f"{selected_network['name']}"
        )

    print(
        f"  Ping:          "
        f"{'Enabled' if ping.upper().startswith('Y') else 'Disabled'}"
    )

    print(
        f"  SNMP:          "
        f"{'Enabled' if snmp.upper().startswith('Y') else 'Disabled'}"
    )

    print(
        f"  Monitoring:    "
        f"{monitoring_mode.upper()}"
    )

    print()

    answer = input(
        "Save changes? (Y/N): "
    ).strip().lower()

    if not answer.startswith("y"):

        print()

        ui.warning(
            "Cancelled."
        )

        print()

        return

    config.update_device(
        device_id,
        name,
        ip,
        ping.upper().startswith("Y"),
        snmp.upper().startswith("Y"),
        network_id=network_id,
        monitoring_mode=monitoring_mode
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

    print()

    ui.success(
        "Device updated successfully."
    )

    print()