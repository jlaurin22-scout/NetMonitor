#!/usr/bin/env python3

import subprocess

import ui
from engine import config
from engine import database
from commands.device.common import add_monitored_device
       
def device_scan():

    from engine.inventory import scanner

    print()
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
    
def show_device(device):

    ui.banner()

    print("Device Details")
    print("--------------")
    print()

    print("General")
    print("-------")
    print()

    print(f"IP Address : {device.ip}")

    if device.hostname:
        print(f"Hostname   : {device.hostname}")

    if device.vendor and device.vendor != "Unknown":
        print(f"Vendor     : {device.vendor}")

    if device.mac:
        print(f"MAC Address: {device.mac}")

    print(f"Type       : {device.device_type}")

    if device.response is not None:
        print(f"Response   : {device.response:.2f} ms")

    if device.model:
        print(f"Model      : {device.model}")

    if device.serial:
        print(f"Serial No. : {device.serial}")

    if device.firmware:
        print(f"Firmware   : {device.firmware}")

    if device.http_server or device.http_title or device.http_protocol:

        print()
        print("HTTP")
        print("----")
        print()

        if device.http_protocol:
            print(f"Protocol : {device.http_protocol}")

        if device.http_server:
            print(f"Server   : {device.http_server}")

        if device.http_title:
            print(f"Title    : {device.http_title}")

    if device.ssh_banner:

        print()
        print("SSH")
        print("---")
        print()

        print(device.ssh_banner)

    if device.snmp:

        print()
        print("SNMP")
        print("----")
        print()

        if device.description:
            print(f"Description : {device.description}")

        if device.location:
            print(f"Location    : {device.location}")

        if device.contact:
            print(f"Contact     : {device.contact}")

        if device.uptime:
            print(f"Uptime      : {device.uptime}")

    if device.ports:

        print()
        print("Ports")
        print("-----")
        print()

        print(", ".join(str(port) for port in sorted(device.ports)))

    print()