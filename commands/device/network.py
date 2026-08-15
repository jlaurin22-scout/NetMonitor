#!/usr/bin/env python3

import subprocess

import ui

from engine import config


def network_list():

    ui.banner("Network List")

    networks = config.get_networks()

    if not networks:

        ui.warning("No networks configured.")
        print()
        return

    print(
        f"{'ID':<4}"
        f"{'NAME':<18}"
        f"{'INTERFACE':<12}"
        f"{'GATEWAY'}"
    )

    print("-" * 60)

    for network in networks:

        print(
            f"{network['id']:<4}"
            f"{network['name']:<18}"
            f"{network['interface']:<12}"
            f"{network['gateway']}"
        )

    print()


def network_remove():

    ui.banner("Remove Network")

    networks = config.get_networks()

    if not networks:

        ui.warning("No networks configured.")
        print()
        return

    print(
        f"{'ID':<4}"
        f"{'NAME':<20}"
        f"{'INTERFACE':<12}"
        f"{'GATEWAY'}"
    )

    print("-" * 65)

    for network in networks:

        print(
            f"{network['id']:<4}"
            f"{network['name']:<20}"
            f"{network['interface']:<12}"
            f"{network['gateway']}"
        )

    print()
    print("C) Cancel")
    print()

    selection = input(
        "Enter network ID: "
    ).strip().lower()

    if selection == "c":

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
    print(
        f"Network: {selected['name']}"
    )
    print(
        f"Interface: {selected['interface']}"
    )
    print(
        f"Gateway: {selected['gateway']}"
    )
    print()

    answer = input(
        "Remove this network? (Y/N): "
    ).strip().lower()

    if not answer.startswith("y"):

        print()
        ui.warning("Cancelled.")
        print()
        return

    try:

        config.remove_network(network_id)

    except Exception as e:

        print()
        ui.error(str(e))
        print()
        return

    subprocess.run(
        ["systemctl", "restart", "netmonitor"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print()
    ui.success(
        f"Network '{selected['name']}' removed successfully."
    )
    print()
    input("Press ENTER to continue...")