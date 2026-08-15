#!/usr/bin/env python3

import subprocess

import ui
from engine import constants


def version():

    ui.banner("Version")

    service = subprocess.run(
        [
            "systemctl",
            "is-active",
            "netmonitor"
        ],
        capture_output=True,
        text=True
    ).stdout.strip()

    print(f"Version : {constants.VERSION}")
    print(f"Build   : {constants.BUILD}")
    print(f"Engine  : {service}")
    print()