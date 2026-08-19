#!/usr/bin/env python3

import ui

from engine import config


def device_list():

    ui.banner("Device List")

    customer = config.load_customer()

    networks = customer.get(
        "networks",
        []
    )

    devices = config.get_devices()

    if not networks and not devices:

        ui.warning("No devices or networks configured.")
        print()
        return

    print(
        f"{'ID':<4} "
        f"{'NAME':<25} "
        f"{'TYPE':<11} "
        f"{'IP ADDRESS'}"
    )

    print("-" * 60)

    for network in networks:

        print(
            f"G{network['id']:<3}"
            f"{network['gateway_name']:<25}"
            f"{'Gateway':<11}"
            f"{network['gateway']}"
        )

    for device in devices:

        print(
            f"{device['id']:<4}"
            f"{device['name']:<25}"
            f"{'Device':<11}"
            f"{device['ip']}"
        )

    print()
