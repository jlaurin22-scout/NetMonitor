#!/usr/bin/env python3

import csv
from pathlib import Path

#
# OUI -> Vendor cache
#
VENDORS = {}


def load_database():
    """
    Load the OUI database.

    Preference:
      1. Debian ieee-data package
      2. Local bundled database
    """

    candidates = [
        Path("/usr/share/ieee-data/oui.csv"),
        Path("/var/lib/ieee-data/oui.csv"),
        Path(__file__).parent / "data" / "oui.csv"
    ]

    csv_file = None

    for candidate in candidates:

        if candidate.exists():

            csv_file = candidate
            break

    if csv_file is None:
        return

    with open(csv_file, newline="", encoding="utf-8") as f:

        reader = csv.reader(f)

        #
        # Skip header if present
        #
        next(reader, None)

        for row in reader:

            #
            # Debian ieee-data format:
            # Registry,Assignment,Organization Name,...
            #
            if len(row) >= 3:

                oui = row[1].strip().upper()
                vendor = row[2].strip()

            #
            # Legacy bundled format:
            # OUI,Vendor
            #
            elif len(row) == 2:

                oui = row[0].strip().upper()
                vendor = row[1].strip()

            else:

                continue

            oui = oui.replace("-", "").replace(":", "")

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
