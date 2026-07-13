#!/usr/bin/env python3

from scheduler import Scheduler
from config import load
from database import initialize
from constants import (
    JOB_GATEWAY,
    JOB_INTERNET,
    JOB_DNS,
    JOB_DEVICE
)


def main():

    initialize()

    config = load()

    customer = config["customer"]
    settings = config["settings"]

    scheduler = Scheduler()

    scheduler.add_job({
        "type": JOB_GATEWAY,
        "name": "Gateway",
        "ip": customer["network"]["gateway"],
        "interval": settings["monitor"]["gateway_interval"]
    })

    scheduler.add_job({
        "type": JOB_INTERNET,
        "name": "Internet",
        "target": settings["internet"]["target"],
        "interval": settings["monitor"]["internet_interval"]
    })

    scheduler.add_job({
        "type": JOB_DNS,
        "name": "DNS",
        "interval": settings["monitor"]["dns_interval"]
    })

    for device in customer["devices"]:

        scheduler.add_job({
            "type": JOB_DEVICE,
            "name": device["name"],
            "ip": device["ip"],
            "device_type": device["type"],
            "interval": settings["monitor"]["device_interval"]
        })

    scheduler.run()


if __name__ == "__main__":
    main()
