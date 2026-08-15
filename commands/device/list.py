#!/usr/bin/env python3

import ui

from engine import config


def device_list():

    ui.banner("Device List")

    devices = config.get_devices()

    if not devices:

        ui.warning("No monitored devices configured.")
        print()
        return

    print(f"{'ID':<4} {'NAME':<25} {'TYPE':<11} {'IP ADDRESS'}")
    print("-" * 60)

    customer = config.load_customer()

    for network in customer["networks"]:

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