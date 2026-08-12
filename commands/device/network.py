#!/usr/bin/env python3

import ui

from engine import config


def network_list():

    ui.banner()

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