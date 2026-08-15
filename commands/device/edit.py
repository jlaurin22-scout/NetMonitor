#!/usr/bin/env python3

import subprocess

import ui

from engine import config


def device_edit():

    ui.banner("Edit Device")

    devices = config.get_devices()

    if not devices:

        ui.warning("No monitored devices configured.")
        print()
        input("Press ENTER to continue...")
        return

    print(f"{'ID':<4} {'NAME':<25} {'IP ADDRESS'}")
    print("-" * 55)

    for device in devices:

        print(
            f"{device['id']:<4}"
            f"{device['name']:<25}"
            f"{device['ip']}"
        )

    print()
    print("C) Cancel")
    print()

    device_selection = input(
        "Enter device ID : "
    ).strip().lower()

    if device_selection == "c":

        return

    try:

        device_id = int(device_selection)

    except ValueError:

        print()
        ui.error("Invalid device ID.")
        print()
        return

    selected = None

    for device in devices:

        if device["id"] == device_id:

            selected = device
            break

    if selected is None:

        print()
        ui.error("Device not found.")
        print()
        return

    print()

    name = input(
        f'Device Name [{selected["name"]}] : '
    ).strip()

    if name == "":

        name = selected["name"]

    ip = input(
        f'IP Address  [{selected["ip"]}] : '
    ).strip()

    if ip == "":

        ip = selected["ip"]

    ping_default = "Y" if selected["checks"]["ping"] else "N"
    snmp_default = "Y" if selected["checks"]["snmp"] else "N"

    ping = input(
        f"Enable Ping (Y/N) [{ping_default}] : "
    ).strip()

    if ping == "":

        ping = ping_default

    snmp = input(
        f"Enable SNMP (Y/N) [{snmp_default}] : "
    ).strip()

    if snmp == "":

        snmp = snmp_default

    print()

    answer = input("Save changes? (Y/N): ").strip().lower()

    if not answer.startswith("y"):

        print()
        ui.warning("Cancelled.")
        print()
        return

    config.update_device(
        device_id,
        name,
        ip,
        ping.upper().startswith("Y"),
        snmp.upper().startswith("Y")
    )

    subprocess.run(
        ["systemctl", "restart", "netmonitor"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print()
    ui.success("Device updated successfully.")
    print()
