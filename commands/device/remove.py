#!/usr/bin/env python3

import subprocess

import ui

from engine import config
from engine import database


def device_remove():

    while True:

        ui.banner("Remove Device")

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

        selection = input(
            "Enter device ID(s) to remove (e.g. 2,5,8): "
        ).strip()

        if not selection:
            return

        removed = 0

        selected_devices = []

        for item in selection.split(","):

            try:
                device_id = int(item.strip())

            except ValueError:
                continue

            for device in devices:

                if device["id"] == device_id:
                    selected_devices.append(device)
                    break

        if not selected_devices:

            print()
            ui.error("No valid devices selected.")
            print()
            input("Press ENTER to continue...")
            continue

        print()
        print("The following devices will be removed:")
        print()

        for device in selected_devices:

            print(f"  {device['name']} ({device['ip']})")

        print()

        answer = input("Proceed? (Y/N): ").strip().lower()

        if not answer.startswith("y"):

            print()
            ui.warning("Cancelled.")
            print()
            input("Press ENTER to continue...")
            return

        for selected in selected_devices:

            config.remove_device(selected["id"])
            database.remove_status(selected["name"])

            ui.success(f"✓ Removed {selected['name']}")
            removed += 1

        if removed:

            print()

            ui.info("Restarting NetMonitor...")

            subprocess.run(
                ["systemctl", "restart", "netmonitor"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            ui.success("Done.")

        print()
        ui.success(f"{removed} device(s) removed.")
        print()

        again = input(
            "Remove more devices? (Y/N): "
        ).strip().lower()

        if not again.startswith("y"):
            return