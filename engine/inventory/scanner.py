#!/usr/bin/env python3

from inventory.network import detect
from inventory.scan import scan_network
from inventory.arp import get_neighbors


def scan():

    info = detect()

    alive = scan_network(info["network"])

    neighbors = get_neighbors()

    devices = []

    for ip in alive:

        devices.append({
            "ip": ip,
            "mac": neighbors.get(ip, "")
        })

    return devices


if __name__ == "__main__":

    devices = scan()

    print()

    print(f"Found {len(devices)} devices")

    print("-" * 35)

    for device in devices:
        print(f"{device['ip']:15} {device['mac']}")
