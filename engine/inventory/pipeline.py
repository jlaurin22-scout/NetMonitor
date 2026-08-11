#!/usr/bin/env python3

from inventory import arp
from inventory import vendor
from inventory import hostname
from inventory import ports
from inventory import http
from inventory import ssh
from inventory import classifier
from inventory.snmp import enrich


class Pipeline:

    def __init__(self):

        self.modules = [
            arp,
            vendor,
            hostname,
            ports,
            http,
            ssh,
            enrich,
            classifier,
        ]

    def get_modules(self):

        return self.modules