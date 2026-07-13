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

        ip = parts[0]

        if "lladdr" not in parts:
            continue

        mac = parts[parts.index("lladdr") + 1].upper()

        neighbors[ip] = mac

    return neighbors


if __name__ == "__main__":

    for ip, mac in sorted(get_neighbors().items()):
        print(f"{ip:15} {mac}")
