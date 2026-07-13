#!/usr/bin/env python3

import subprocess


def get_neighbors():
    """
    Returns a dictionary of IP -> MAC addresses
    from the Linux neighbor table.
    """

    neighbors = {}

    output = subprocess.check_output(
        ["ip", "neigh"],
        text=True
    ).splitlines()

    for line in output:

        parts = line.split()

        if len(parts) < 5:
            continue

        if "lladdr" not in parts:
            continue

        ip = parts[0]
        mac = parts[parts.index("lladdr") + 1].upper()

        neighbors[ip] = mac

    return neighbors


#
# Cache the ARP table once per scan.
#
_NEIGHBORS = None


def enrich(device):
    """
    Populate the MAC address of a device.
    """

    global _NEIGHBORS

    if _NEIGHBORS is None:
        _NEIGHBORS = get_neighbors()

    device.mac = _NEIGHBORS.get(device.ip, "")
