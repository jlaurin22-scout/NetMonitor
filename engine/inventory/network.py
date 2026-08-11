#!/usr/bin/env python3

import ipaddress
import subprocess


def detect():

    networks = []

    #
    # Read all IPv4 interfaces
    #
    addr = subprocess.check_output(
        ["ip", "-o", "-f", "inet", "addr", "show"],
        text=True
    ).splitlines()

    #
    # Read routing table once
    #
    routes = subprocess.check_output(
        ["ip", "route"],
        text=True
    ).splitlines()

    for line in addr:

        if "scope global" not in line:
            continue

        fields = line.split()

        interface_name = fields[1]

        #
        # Ignore virtual interfaces.
        #
        if (
            interface_name == "lo"
            or
            interface_name.startswith("tailscale")
            or
            interface_name.startswith("docker")
            or
            interface_name.startswith("br-")
            or
            interface_name.startswith("virbr")
            or
            interface_name.startswith("tun")
            or
            interface_name.startswith("wg")
        ):

            continue
            
        cidr = fields[3]

        interface = ipaddress.ip_interface(cidr)

        gateway = ""

        #
        # First look for a default gateway.
        #
        for route in routes:

            if (
                route.startswith("default")
                and
                f"dev {interface_name}" in route
            ):

                gateway = route.split()[2]
                break

        #
        # If there is no default gateway on this interface,
        # leave it empty. The initialization wizard will ask
        # the user for the correct gateway.
        #
        if gateway == "":

            gateway = ""
            
        networks.append(
            {
                "interface": interface_name,
                "ip": str(interface.ip),
                "gateway": gateway,
                "network": str(interface.network),
                "prefix": interface.network.prefixlen,
                "dns": [
                    gateway,
                    "1.1.1.1"
                ]
            }
        )

    return networks

if __name__ == "__main__":

    detected = detect()

    for info in detected:

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