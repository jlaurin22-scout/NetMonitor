#!/usr/bin/env python3

import subprocess

import ui
from engine import config
from engine import database

def add_monitored_device(name, ip, ping=True, snmp=False):

    config.add_device(
        name=name,
        ip=ip,
        ping=ping,
        snmp=snmp
    )

def device_add():

    ui.banner()

    print("Add Monitored Device")
    print("--------------------")

    name = input("Device Name : ").strip()
    ip = input("IP Address  : ").strip()

    print()

    ping = input("Enable Ping monitoring? (Y/N): ").lower().startswith("y")
    snmp = input("Enable SNMP monitoring? (Y/N): ").lower().startswith("y")

    try:
        add_monitored_device(name, ip, ping, snmp)

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

def device_list():

    ui.banner()

    devices = config.get_devices()

    if not devices:

        ui.warning("No monitored devices configured.")
        print()
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
    
def network_list():

    ui.banner()

    networks = config.get_networks()

    if not networks:

        ui.warning("No networks configured.")
        print()
        return

    print(
        f"{'ID':<4} "
        f"{'NAME':<18} "
        f"{'INTERFACE':<12} "
        f"{'GATEWAY'}"
    )

    print("-" * 60)

    for network in networks:

        print(
            f"{network['id']:<4}"
            f"{network['name']:<18}"
            f"{network['interface']:<12}"
            f"{network['gateway']}"
        )

    print()

def device_remove():

    while True:

        ui.banner()

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
            "Remove another device? (Y/N): "
        ).strip().lower()

        if not again.startswith("y"):

            return
            
def device_edit():

    ui.banner()

    devices = config.get_devices()

    if not devices:

        ui.warning("No monitored devices configured.")
        print()
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

    device_id = int(input("Enter device ID : "))

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
    print("Device updated successfully.")
    print()

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

    for item in selection.split(","):

        try:

            index = int(item.strip()) - 1

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

            print(f"DEBUG: Adding '{name}' ({device.ip})")

            add_monitored_device(
                name=name,
                ip=device.ip,
                ping=True,
                snmp=device.snmp
            )

            print("DEBUG: Device added")
            
            ui.success(f"✓ Added {name}")

            added += 1

        except Exception as e:

            import traceback

            traceback.print_exc()

            print()

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