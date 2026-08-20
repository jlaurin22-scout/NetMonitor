#!/usr/bin/env python3

import ipaddress
import subprocess


def get_dhcp_dns(interface_name):

    lease_file = (
        f"/var/lib/dhcp/dhclient.{interface_name}.leases"
    )

    try:

        with open(lease_file, "r") as f:

            content = f.read()

    except OSError:

        return []

    leases = content.split("lease {")

    for lease in reversed(leases):

        if f'interface "{interface_name}"' not in lease:

            continue

        dns_servers = []

        for line in lease.splitlines():

            line = line.strip()

            if not line.startswith(
                "option domain-name-servers"
            ):

                continue

            value = line.split(
                " ",
                2
            )[-1].rstrip(";")

            for server in value.split():

                if server not in dns_servers:

                    dns_servers.append(server)

        if dns_servers:

            return dns_servers

    return []


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
        dns = get_dhcp_dns(
            interface_name
        )

        if not dns:

            dns = [
                gateway,
                "1.1.1.1"
            ]

        networks.append(
            {
                "interface": interface_name,
                "ip": str(interface.ip),
                "gateway": gateway,
                "network": str(interface.network),
                "prefix": interface.network.prefixlen,
                "dns": dns
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
        print(
            f"DNS       : "
            f"{', '.join(info['dns'])}"
        )

    print()