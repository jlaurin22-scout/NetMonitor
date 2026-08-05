#!/usr/bin/env python3

import time
from notify import send_startup_ip
from scheduler import Scheduler
from config import load, get_devices
from database import initialize, sync_status
from constants import (
    JOB_GATEWAY,
    JOB_INTERNET,
    JOB_DNS,
    JOB_DEVICE
)


def dns_display_name(server):

    if server in ("1.1.1.1", "1.0.0.1"):
        return "Cloudflare DNS"

    if server in ("8.8.8.8", "8.8.4.4"):
        return "Google DNS"

    if server == "9.9.9.9":
        return "Quad9 DNS"

    return "DNS"


def main():

    print()
    print("============================================================")
    print("              NetMonitor Engine v0.4.0")
    print("============================================================")
    print()

    print("Initializing database...")
    initialize()

    send_startup_ip()

    print("Loading configuration...")
    config = load()

    if "gateway" not in config["customer"]["network"]:

        print()
        print("NetMonitor has not been initialized.")
        print("Run 'nm init' to configure this appliance.")
        print("Waiting for configuration...")
        print()

        while True:
            time.sleep(60)

    customer = config["customer"]
    settings = config["settings"]

    gateway_name = customer["network"].get(
        "gateway_name",
        "Gateway"
    )

    dns_name = dns_display_name(
        settings["dns"]["server"]
    )

    scheduler = Scheduler()

    print("Adding Gateway monitor...")
    scheduler.add_job({
        "type": JOB_GATEWAY,
        "name": gateway_name,
        "ip": customer["network"]["gateway"],
        "interval": settings["monitor"]["gateway_interval"]
    })

    print("Adding Internet monitor...")
    scheduler.add_job({
        "type": JOB_INTERNET,
        "name": "Internet",
        "targets": settings["internet"]["targets"],
        "interval": settings["monitor"]["internet_interval"]
    })

    print("Adding DNS monitor...")
    scheduler.add_job({
        "type": JOB_DNS,
        "name": dns_name,
        "server": settings["dns"]["server"],
        "lookup": settings["dns"]["lookup"],
        "interval": settings["monitor"]["dns_interval"]
    })

    devices = get_devices()

    valid_jobs = [
        gateway_name,
        "Internet",
        dns_name
    ]

    valid_jobs.extend(
        device["name"] for device in devices
    )

    sync_status(valid_jobs)

    print(f"Adding {len(devices)} device monitor(s)...")

    for device in devices:

        print(f"  - {device['name']} ({device['ip']})")

        scheduler.add_job({
            "type": JOB_DEVICE,
            "name": device["name"],
            "ip": device["ip"],
            "checks": device["checks"],
            "interval": settings["monitor"]["device_interval"]
        })

    print()
    print("Engine started successfully.")
    print()

    try:
        scheduler.run()

    except KeyboardInterrupt:
        print()
        print("Stopping NetMonitor...")
        print("Goodbye.")
        print()


if __name__ == "__main__":
    main()