#!/usr/bin/env python3

import subprocess

import ui

from .common import add_monitored_device


def device_add():

    ui.banner()

    print("Add Monitored Device")
    print("--------------------")

    name = input("Device Name : ").strip()
    ip = input("IP Address  : ").strip()

    print()

    ping = input(
        "Enable Ping monitoring? (Y/N): "
    ).lower().startswith("y")

    snmp = input(
        "Enable SNMP monitoring? (Y/N): "
    ).lower().startswith("y")

    try:

        add_monitored_device(
            name,
            ip,
            ping,
            snmp
        )

    except Exception as e:

        print()
        ui.error(str(e))
        print()
        return

    print()

    ui.success("Device added successfully.")

    ui.info("Restarting NetMonitor...")

    subprocess.run(
        ["systemctl", "restart", "netmonitor"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    ui.success("Done.")

    print()