#!/usr/bin/env python3

import ui

from engine import config


def get_network_devices(
    network,
    devices
):

    network_id = network["id"]

    return [
        device
        for device in devices
        if device.get("network_id") == network_id
    ]


def device_list():

    ui.banner("Device List")

    networks = config.get_networks()
    devices = config.get_devices()

    if not networks and not devices:

        ui.warning(
            "No devices or networks configured."
        )

        print()

        return

    for network in networks:

        network_name = network["name"]

        print()
        print(network_name)

        print("-" * 80)

        print(
            f"{'ID':<4}"
            f"{'NAME':<25}"
            f"{'MODE':<11}"
            f"{'IP ADDRESS'}"
        )

        print("-" * 80)

        gateway_id = (
            f"G{network['id']}"
        )

        print(
            f"{gateway_id:<4}"
            f"{network['gateway_name']:<25}"
            f"{'GATEWAY':<11}"
            f"{network['gateway']}"
        )

        network_devices = get_network_devices(
            network,
            devices
        )

        for device in network_devices:

            monitoring_mode = (
                config.get_device_monitoring_mode(
                    device
                )
            )

            print(
                f"{device['id']:<4}"
                f"{device['name']:<25}"
                f"{monitoring_mode.upper():<11}"
                f"{device['ip']}"
            )

    unassigned_devices = [
        device
        for device in devices
        if not any(
            device.get("network_id")
            == network["id"]
            for network in networks
        )
    ]

    if unassigned_devices:

        print()
        print("UNASSIGNED")
        print("-" * 80)

        print(
            f"{'ID':<4}"
            f"{'NAME':<25}"
            f"{'MODE':<11}"
            f"{'IP ADDRESS'}"
        )

        print("-" * 80)

        for device in unassigned_devices:

            monitoring_mode = (
                config.get_device_monitoring_mode(
                    device
                )
            )

            print(
                f"{device['id']:<4}"
                f"{device['name']:<25}"
                f"{monitoring_mode.upper():<11}"
                f"{device['ip']}"
            )

    print()