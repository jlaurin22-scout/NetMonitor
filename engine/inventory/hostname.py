#!/usr/bin/env python3

import socket


def lookup(ip):
    """
    Resolve an IP address using reverse DNS.
    """

    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname.split(".")[0]

    except Exception:
        return ""


def enrich(device):
    """
    Populate the hostname of a device.
    """

    device.hostname = lookup(device.ip)


if __name__ == "__main__":

    while True:

        ip = input("IP Address: ").strip()

        if not ip:
            break

        print(lookup(ip))
