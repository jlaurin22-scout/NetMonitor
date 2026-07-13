#!/usr/bin/env python3

import subprocess

from inventory import scanner


class Monitor:

    def __init__(self, interval=300):
        self.interval = interval
        self.devices = []
        self.state = {}

        print(f"Monitor initialized (interval: {self.interval}s)")

    def get_key(self, device):

        if device.mac:
            return device.mac

        return device.ip

    def discover(self):

        self.devices = scanner.scan()

        print(f"Discovered {len(self.devices)} devices")
        print()

        for device in self.devices:

            self.state[self.get_key(device)] = {
                "status": None
            }

            print(f"{device.ip:15} {device.hostname}")

    def check(self, device):

        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", device.ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        key = self.get_key(device)

        if result.returncode == 0:
            self.state[key]["status"] = "UP"
        else:
            self.state[key]["status"] = "DOWN"

        return self.state[key]["status"]
