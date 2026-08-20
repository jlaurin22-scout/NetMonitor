#!/usr/bin/env python3

import socket
import subprocess

import dns.resolver
import dns.reversename


def reverse_dns(ip, servers=None):

    if servers:

        reverse_name = dns.reversename.from_address(ip)

        for server in servers:

            if not server:
                continue

            resolver = dns.resolver.Resolver(
                configure=False
            )

            resolver.nameservers = [
                server
            ]

            resolver.timeout = 2
            resolver.lifetime = 2

            try:

                answers = resolver.resolve(
                    reverse_name,
                    "PTR"
                )

                for answer in answers:

                    hostname = str(answer).rstrip(".")

                    if hostname:

                        return hostname.split(".")[0]

            except Exception:

                continue

        return ""

    try:

        hostname = socket.gethostbyaddr(ip)[0]

        return hostname.split(".")[0]

    except Exception:

        return ""


def netbios(ip):

    try:

        output = subprocess.check_output(
            ["nmblookup", "-A", ip],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2
        )

        for line in output.splitlines():

            if "<00>" in line and "<GROUP>" not in line:

                return line.split()[0]

    except Exception:

        pass

    return ""


def mdns(ip):

    try:

        output = subprocess.check_output(
            ["avahi-resolve-address", ip],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2
        )

        parts = output.strip().split()

        if len(parts) >= 2:

            hostname = parts[1].split(".")[0]

            #
            # Ignore systemd machine-id hostnames
            #
            if (
                len(hostname) == 36
                and
                hostname.count("-") == 4
            ):

                return ""

            return hostname

    except Exception:

        pass

    return ""


def lookup(ip, servers=None):

    #
    # Explicit DNS
    #

    hostname = reverse_dns(
        ip,
        servers
    )

    if hostname:

        return hostname

    #
    # NetBIOS
    #

    hostname = netbios(ip)

    if hostname:

        return hostname

    #
    # mDNS / Avahi
    #

    hostname = mdns(ip)

    if hostname:

        return hostname

    return ""


def enrich(device):

    if device.hostname:
        return

    device.hostname = lookup(
        device.ip,
        device.dns_servers
    )


if __name__ == "__main__":

    while True:

        ip = input("IP Address: ").strip()

        if not ip:
            break

        print(lookup(ip))