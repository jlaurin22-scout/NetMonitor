#!/usr/bin/env python3

import subprocess

import ui
from engine import config


def version():

    ui.banner()

    try:

        customer = config.load_customer()

        version = customer.get(
            "version",
            "Unknown"
        )

    except Exception:

        version = "Unknown"

    build = "0.5.0-dev1"

    service = subprocess.run(
        [
            "systemctl",
            "is-active",
            "netmonitor"
        ],
        capture_output=True,
        text=True
    ).stdout.strip()

    print(f"Version : {version}")
    print(f"Build   : {build}")
    print(f"Engine  : {service}")
    print()