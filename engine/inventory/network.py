#!/usr/bin/env python3

import ipaddress
import subprocess


def detect():

    # Get interface address (includes prefix length)
    addr = subprocess.check_output(
        ["ip", "-o", "-f", "inet", "addr", "show"],
        text=True
    ).splitlines()

    ip = ""
    network = None

    for line in addr:
        if "scope global" in line:
            cidr = line.split()[3]          # e.g. 192.168.75.29/24
            interface = ipaddress.ip_interface(cidr)

            ip = str(interface.ip)
            network = interface.network
            break

    # Get default gateway
    gateway = ""

    routes = subprocess.check_output(
        ["ip", "route"],
        text=True
    ).splitlines()

    for line in routes:
        if line.startswith("default"):
            gateway = line.split()[2]
            break

    return {
        "ip": ip,
        "gateway": gateway,
        "network": str(network),
        "prefix": network.prefixlen,
    }


if __name__ == "__main__":

    info = detect()

    print()
    print("Detected Network")
    print("----------------")
    print(f"IP       : {info['ip']}")
    print(f"Gateway  : {info['gateway']}")
    print(f"Network  : {info['network']}")
    print(f"Prefix   : /{info['prefix']}")
    print()
