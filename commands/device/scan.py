#!/usr/bin/env python3

import subprocess

import ui
from commands.device.common import add_monitored_device


def device_scan():

    from engine.inventory import scanner

    ui.banner("Device Scan")

    ui.info("Scanning network...")
    print()

    devices = scanner.scan()

    if not devices:

        ui.warning("No devices found.")
        return

    print(
        f"{'#':>2} "
        f"{'IP Address':15} "
        f"{'Vendor':40} "
        f"{'Hostname':22} "
        f"{'Type':18}"
    )

    print("-" * 105)

    for i, device in enumerate(devices, 1):

        print(
            f"{i:>2} "
            f"{device.ip:15} "
            f"{device.vendor[:40]:40} "
            f"{device.hostname[:22]:22} "
            f"{device.device_type[:18]:18}"
        )

    print()

    selection = input(
        "Select device(s) to add (e.g. 1,3,5 or Enter to cancel): "
    ).strip()

    if not selection:
        return

    added = 0

    selected_indexes = []

    for item in selection.split(","):

        item = item.strip()

        if "-" in item:

            try:

                start, end = item.split("-", 1)

                start = int(start)
                end = int(end)

                if start > end:

                    start, end = end, start

                for number in range(start, end + 1):

                    if number not in selected_indexes:

                        selected_indexes.append(number)

            except ValueError:

                continue

        else:

            try:

                number = int(item)

                if number not in selected_indexes:

                    selected_indexes.append(number)

            except ValueError:

                continue

    for number in selected_indexes:

        try:

            index = number - 1

            if index < 0 or index >= len(devices):
                continue

            device = devices[index]

            default_name = device.hostname.strip()

            if not default_name or default_name.lower() == "unknown":

                default_name = device.ip

            print()

            name = input(
                f"Name [{default_name}]: "
            ).strip()

            if not name:

                name = default_name

            add_monitored_device(
                name=name,
                ip=device.ip,
                ping=True,
                snmp=device.snmp
            )

            ui.success(f"✓ Added {name}")

            added += 1

        except Exception as e:

            ui.error(str(e))

            input("Press ENTER...")

    if added:

        print()

        ui.info("Restarting NetMonitor...")

        subprocess.run(
            ["systemctl", "restart", "netmonitor"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        ui.success("Done.")

    print()
    print(f"{added} device(s) added.")