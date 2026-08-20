#!/usr/bin/env python3

import ipaddress

from inventory.device import Device
from inventory.network import detect
from inventory.scan import scan_network
from inventory.pipeline import Pipeline
from inventory.executor import Executor
from engine.config import get_networks


def find_network_id(ip, networks):

    address = ipaddress.ip_address(ip)

    for network in networks:

        try:

            configured_network = ipaddress.ip_network(
                f"{network['ip']}/{network['prefix']}",
                strict=False
            )

        except (KeyError, ValueError):

            continue

        if address in configured_network:

            return network["id"]

    return None


def scan():

    detected_networks = detect()
    configured_networks = get_networks()

    alive = []

    for network in detected_networks:

        hosts = scan_network(
            network["network"]
        )

        for host in hosts:

            host["dns_servers"] = network["dns"]

            host["network_id"] = find_network_id(
                host["ip"],
                configured_networks
            )

        alive.extend(hosts)

    devices = []

    for host in alive:

        device = Device(ip=host["ip"])
        device.response = host["response"]

        device.dns_servers = host.get(
            "dns_servers",
            []
        )

        device.network_id = host.get(
            "network_id"
        )

        devices.append(device)

    executor = Executor(
        Pipeline().get_modules(),
        workers=25
    )

    executor.enrich(devices)

    return devices


if __name__ == "__main__":

    devices = scan()

    print()
    print("=" * 100)
    print("NetMonitor Inventory")
    print("=" * 100)
    print()

    print(f"Found {len(devices)} devices")
    print()

    print(
        f"{'IP Address':15} "
        f"{'Hostname':22} "
        f"{'Type':18} "
        f"{'Response':10} "
        f"{'Vendor':15} "
        f"{'SNMP':5}"
    )

    print("-" * 100)

    for device in devices:

        snmp = "Yes" if device.snmp else "No"

        print(
            f"{device.ip:15} "
            f"{device.hostname[:22]:22} "
            f"{device.device_type:18} "
            f"{device.response_string():>10} "
            f"{device.vendor[:15]:15} "
            f"{snmp:5}"
        )

        #
        # Show SNMP information when available
        #
        if device.snmp:

            if device.description:
                print(f"    Description : {device.description}")

            if device.location:
                print(f"    Location    : {device.location}")

            if device.contact:
                print(f"    Contact     : {device.contact}")

            print()

    print("-" * 100)