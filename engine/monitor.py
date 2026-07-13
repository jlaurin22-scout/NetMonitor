#!/usr/bin/env python3

from inventory import scanner


class Monitor:

    def __init__(self, interval=300):
        self.interval = interval
        self.devices = []

        print(f"Monitor initialized (interval: {self.interval}s)")

    def discover(self):

        self.devices = scanner.scan()

        print(f"Discovered {len(self.devices)} devices")
