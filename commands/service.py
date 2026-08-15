#!/usr/bin/env python3

import subprocess

import ui


def service():

    ui.banner("NetMonitor Service")

    active = subprocess.run(
        ["systemctl", "is-active", "netmonitor"],
        capture_output=True,
        text=True
    ).stdout.strip()

    enabled = subprocess.run(
        ["systemctl", "is-enabled", "netmonitor"],
        capture_output=True,
        text=True
    ).stdout.strip()

    pid = subprocess.run(
        [
            "systemctl",
            "show",
            "-p",
            "MainPID",
            "--value",
            "netmonitor"
        ],
        capture_output=True,
        text=True
    ).stdout.strip()

    uptime = subprocess.run(
        [
            "systemctl",
            "show",
            "-p",
            "ActiveEnterTimestamp",
            "--value",
            "netmonitor"
        ],
        capture_output=True,
        text=True
    ).stdout.strip()

    status = "UP" if active == "active" else "DOWN"
    print(f"Status  : {ui.state(status)}")

    enabled_state = "UP" if enabled == "enabled" else "DOWN"
    print(f"Enabled : {ui.state(enabled_state)}")

    print(f"PID     : {pid}")
    print(f"Started : {uptime}")
    print()