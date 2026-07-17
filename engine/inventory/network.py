#!/usr/bin/env python3

import ipaddress
import subprocess


def detect():

    interface_name = ""
    ip = ""
    network = None

    #
    # Get interface, IP address and network
    #
    addr = subprocess.check_output(
        ["ip", "-o", "-f", "inet", "addr", "show"],
        text=True
    ).splitlines()

    for line in addr:

        if "scope global" not in line:
            continue

        fields = line.split()

        interface_name = fields[1]

        cidr = fields[3]

        interface = ipaddress.ip_interface(cidr)

        ip = str(interface.ip)
        network = interface.network

        break

    #
    # Get default gateway
    #
    gateway = ""

    routes = subprocess.check_output(
        ["ip", "route"],
        text=True
    ).splitlines()

    for line in routes:

        if line.startswith("default"):

            gateway = line.split()[2]
            break

    #
    # Use sensible default DNS servers
    #
    dns = [
        gateway,
        "1.1.1.1"
    ]

    return {
        "interface": interface_name,
        "ip": ip,
        "gateway": gateway,
        "network": str(network),
        "prefix": network.prefixlen,
        "dns": dns
    }


if __name__ == "__main__":

    info = detect()

    print()
    print("Detected Network")
    print("----------------")
    print(f"Interface : {info['interface']}")
    print(f"IP        : {info['ip']}")
    print(f"Gateway   : {info['gateway']}")
    print(f"Network   : {info['network']}")
    print(f"Prefix    : /{info['prefix']}")
    print(f"DNS 1     : {info['dns'][0]}")
    print(f"DNS 2     : {info['dns'][1]}")
    print()
