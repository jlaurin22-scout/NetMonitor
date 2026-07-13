#!/usr/bin/env python3

import json

CUSTOMER_CONFIG = "/etc/netmonitor/netmonitor.json"
SETTINGS_CONFIG = "/etc/netmonitor/settings.json"


def load():

    with open(CUSTOMER_CONFIG, "r") as f:
        customer = json.load(f)

    with open(SETTINGS_CONFIG, "r") as f:
        settings = json.load(f)

    return {
        "customer": customer,
        "settings": settings
    }
