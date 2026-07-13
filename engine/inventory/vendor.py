#!/usr/bin/env python3

import csv
from pathlib import Path

#
# OUI -> Vendor cache
#
VENDORS = {}


def load_database():
    """
    Load the local OUI database.
    """

    csv_file = Path(__file__).parent / "data" / "oui.csv"

    if not csv_file.exists():
        return

    with open(csv_file, newline="", encoding="utf-8") as f:

        reader = csv.reader(f)

        for row in reader:

            if len(row) != 2:
                continue

            oui = row[0].strip().upper()
            vendor = row[1].strip()

            VENDORS[oui] = vendor


def lookup(mac):
    """
    Return the vendor for a MAC address.
    """

    if not mac:
        return "Unknown"

    oui = mac.upper().replace(":", "")[:6]

    return VENDORS.get(oui, "Unknown")


def enrich(device):
    """
    Populate the vendor name for a device.
    """

    device.vendor = lookup(device.mac)


#
# Load the database once.
#
load_database()


if __name__ == "__main__":

    tests = [
        "00:0C:29:AA:BB:CC",
        "00:08:9B:11:22:33",
        "68:05:CA:AA:BB:CC",
        "24:5E:BE:12:34:56",
        "AA:BB:CC:DD:EE:FF",
        ""
    ]

    for mac in tests:
        print(f"{mac:20} -> {lookup(mac)}")
