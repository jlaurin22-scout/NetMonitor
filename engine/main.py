#!/usr/bin/env python3

import time
from engine.notify import send_startup_ip
from engine.scheduler import Scheduler
from engine.config import load, get_devices
from engine.database import initialize, sync_status
from engine.constants import (
    JOB_GATEWAY,
    JOB_INTERNET,
    JOB_DNS,
    JOB_DEVICE,
    VERSION,
    BUILD
)
from engine.network import (
    setup_network_routes,
    cleanup_network_routes
)


def dns_display_name(server):

    if server in ("1.1.1.1", "1.0.0.1"):
        return "Cloudflare DNS"

    if server in ("8.8.8.8", "8.8.4.4"):
        return "Google DNS"

    if server == "9.9.9.9":
        return "Quad9 DNS"

    return "DNS"


def add_network_monitors(
    scheduler,
    network,
    settings
):

    gateway_name = network.get(
        "gateway_name",
        "Gateway"
    )

    internet_name = (
        f"{network['name']} Internet"
    )

    dns_name = (
        f"{network['name']} DNS"
    )

    print("Adding Gateway monitor...")

    scheduler.add_job({
        "type": JOB_GATEWAY,
        "name": gateway_name,
        "network_id": network["id"],
        "network": network,
        "ip": network["gateway"],
        "interval": settings["monitor"]["gateway_interval"]
    })

    print("Adding Internet monitor...")

    scheduler.add_job({
        "type": JOB_INTERNET,
        "name": internet_name,
        "network_id": network["id"],
        "network": network,
        "targets": settings["internet"]["targets"],
        "interval": settings["monitor"]["internet_interval"]
    })

    print("Adding DNS monitor...")

    scheduler.add_job({
        "type": JOB_DNS,
        "name": dns_name,
        "network_id": network["id"],
        "network": network,
        "server": network["dns"][0],
        "lookup": settings["dns"]["lookup"],
        "interval": settings["monitor"]["dns_interval"]
    })

    return [
        gateway_name,
        internet_name,
        dns_name
    ]


def main():

    print()
    print("============================================================")
    print(
        f"              NetMonitor Engine v{VERSION}-{BUILD}"
    )
    print("============================================================")
    print()

    print("Initializing database...")
    initialize()

    send_startup_ip()

    print("Loading configuration...")
    config = load()

    if (
        "networks" not in config["customer"]
        or
        len(config["customer"]["networks"]) == 0
    ):

        print()
        print("NetMonitor has not been initialized.")
        print("Run 'nm init' to configure this appliance.")
        print("Waiting for configuration...")
        print()

        while True:
            time.sleep(60)

    customer = config["customer"]
    settings = config["settings"]

    networks = customer["networks"]

    setup_network_routes(networks)

    scheduler = Scheduler()

    valid_jobs = []

    for network in networks:

        print()
        print(
            f"Adding network monitor: {network['name']}"
        )

        network_jobs = add_network_monitors(
            scheduler,
            network,
            settings
        )

        valid_jobs.extend(network_jobs)

    print()

    print()

    devices = get_devices()

    print(
        f"Adding {len(devices)} device monitor(s)..."
    )

    for device in devices:

        network_id = device.get(
            "network_id",
            1
        )

        print(
            f"  - {device['name']} "
            f"({device['ip']}) "
            f"[Network {network_id}]"
        )

        job_name = (
            f"{network_id}:"
            f"{device['name']}"
        )

        valid_jobs.append(
            job_name
        )

        network = None

        for configured_network in networks:

            if configured_network["id"] == network_id:

                network = configured_network
                break

        if network is None:

            print(
                f"  - Skipping {device['name']}: "
                f"Network {network_id} not found."
            )

            continue

        scheduler.add_job({
            "type": JOB_DEVICE,
            "name": job_name,
            "network_id": network_id,
            "network": network,
            "ip": device["ip"],
            "checks": device["checks"],
            "interval": settings["monitor"]["device_interval"]
        })

    sync_status(valid_jobs)

    print()
    print("Engine started successfully.")
    print()

    try:

        scheduler.run()

    except KeyboardInterrupt:

        print()
        print("Stopping NetMonitor...")
        print("Goodbye.")

    finally:

        cleanup_network_routes(networks)


if __name__ == "__main__":
    main()