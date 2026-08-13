#!/usr/bin/env python3

from engine.inventory.network import detect
import ui


def run():

    detected = detect()

    if len(detected) == 0:

        ui.error("No usable network interfaces were detected.")
        print()

        return None

    configured = []
    networks = []

    while True:

        print("Detected Interfaces")
        print("-------------------")
        print()

        available = []
        index = 1

        for interface in detected:

            if interface["interface"] in configured:
                continue

            available.append(interface)

            print(
                f"{index}) "
                f"{interface['interface']:<8}"
                f"{interface['ip']}/{interface['prefix']}    "
                f"Gateway: {interface['gateway']}"
            )

            index += 1

        if len(available) == 0:
            break

        print()

        try:

            selection = int(
                input("Select interface: ").strip()
            )

        except ValueError:

            print()
            ui.error("Invalid selection.")
            print()
            continue

        if selection < 1 or selection > len(available):

            print()
            ui.error("Invalid selection.")
            print()
            continue

        info = available[selection - 1]

        print()
        print("Network Configuration")
        print("---------------------")

        network_name = input(
            "Network Name : "
        ).strip()

        if network_name == "":

            network_name = info["interface"]

        gateway_name = input(
            "Router / Firewall : "
        ).strip()

        if gateway_name == "":

            gateway_name = "Router / Firewall"

        gateway = info["gateway"]

        if gateway == "":

            print()
            print(
                "No gateway was automatically detected."
            )

            while True:

                gateway = input(
                    "Gateway IP : "
                ).strip()

                if gateway != "":

                    break

        print()
        print("Detected Settings")
        print("-----------------")
        print(f"Interface : {info['interface']}")
        print(f"IP        : {info['ip']}")
        print(f"Prefix    : /{info['prefix']}")
        print(f"Gateway   : {gateway}")
        print(f"DNS 1     : {gateway}")
        print("DNS 2     : 1.1.1.1")
        print()

        answer = input(
            "Use these settings? (Y/N): "
        ).strip().lower()

        if not answer.startswith("y"):

            print()
            ui.warning("Interface skipped.")
            print()
            continue

        configured.append(info["interface"])

        networks.append(
            {
                "id": len(networks) + 1,
                "name": network_name,
                "interface": info["interface"],
                "ip": info["ip"],
                "prefix": info["prefix"],
                "gateway": gateway,
                "gateway_name": gateway_name,
                "dns": [
                    gateway,
                    "1.1.1.1"
                ]
            }
        )

        if len(configured) == len(detected):
            break

        print()

        answer = input(
            "Add another network? (Y/N): "
        ).strip().lower()

        print()

        if not answer.startswith("y"):
            break

    return networks


