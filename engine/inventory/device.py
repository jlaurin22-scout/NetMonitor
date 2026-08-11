#!/usr/bin/env python3

"""
NetMonitor Device

Represents a discovered network device.
"""


class Device:

    def __init__(self, ip=""):

        #
        # Discovery
        #
        self.ip = ip
        self.mac = ""
        self.hostname = ""
        self.vendor = "Unknown"

        #
        # Ping
        #
        self.response = None

        #
        # Port scan
        #
        self.ports = []

        #
        # HTTP
        #
        self.http_server = ""
        self.http_title = ""
        self.http_protocol = ""

        #
        # SSH
        #
        self.ssh_banner = ""

        #
        # Classification
        #
        self.device_type = "Unknown"

        #
        # SNMP
        #
        self.snmp = False
        self.description = ""
        self.uptime = None
        self.contact = ""
        self.location = ""

        #
        # Vendor specific
        #
        self.model = ""
        self.firmware = ""
        self.serial = ""

    def response_string(self):

        if self.response is None:
            return "Timeout"

        return f"{self.response:.2f} ms"

    def to_dict(self):

        return {

            "ip": self.ip,
            "mac": self.mac,
            "hostname": self.hostname,
            "vendor": self.vendor,
            "response": self.response,
            "ports": self.ports,

            "http_server": self.http_server,
            "http_title": self.http_title,
            "http_protocol": self.http_protocol,

            "ssh_banner": self.ssh_banner,

            "device_type": self.device_type,

            "snmp": self.snmp,
            "description": self.description,
            "uptime": self.uptime,
            "contact": self.contact,
            "location": self.location,

            "model": self.model,
            "firmware": self.firmware,
            "serial": self.serial,

        }

    def __repr__(self):

        return (
            f"<Device "
            f"{self.ip} "
            f"{self.hostname} "
            f"{self.device_type}>"
        )