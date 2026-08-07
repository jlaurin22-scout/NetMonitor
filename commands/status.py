#!/usr/bin/env python3

import subprocess

import ui
from engine import config
from engine import database


def status():

    ui.banner()

    customer = config.load_customer()

    print("Customer")
    print("--------")
    print(f"Customer : {customer.get('customer','Unknown')}")
    print(f"Site     : {customer.get('site','Unknown')}")
    print()

    service = subprocess.run(
        ["systemctl", "is-active", "netmonitor"],
        capture_output=True,
        text=True
    ).stdout.strip()

    print("Service")
    print("-------")

    service_state = (
        "UP"
        if service == "active"
        else "DOWN"
    )

    print(f"Status   : {ui.state(service_state)}")

    print()
    print("Current Status")
    print("--------------")

    rows = database.get_current_status()

    print(
        f"{'NAME':<25} "
        f"{'TYPE':<10} "
        f"{'STATE':<18} "
        "LAST CHANGE"
    )

    print("-" * 75)

    for row in rows:

        name = row["job_name"]

        if ":" in name:

            name = name.split(
                ":",
                1
            )[1]

        if len(name) > 25:

            name = name[:22] + "..."

        print(
            f"{name:<25}"
            f"{row['job_type']:<10}"
            f"{ui.state(row['state']):<18}"
            f"{row['last_change']}"
        )

    print()