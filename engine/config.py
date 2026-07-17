#!/usr/bin/env python3

import json
import ipaddress

CUSTOMER_CONFIG = "/etc/netmonitor/netmonitor.json"
DEVICES_CONFIG = "/etc/netmonitor/devices.json"
SETTINGS_CONFIG = "/etc/netmonitor/settings.json"

def validate_ip(ip):

    try:

        ipaddress.ip_address(ip)

    except ValueError:

        raise Exception(
            f"Invalid IP address: {ip}"
        )

#
# Customer Configuration
#

def load_customer():

    with open(CUSTOMER_CONFIG, "r") as f:
        return json.load(f)


def save_customer(data):

    with open(CUSTOMER_CONFIG, "w") as f:
        json.dump(data, f, indent=4)


#
# Device Configuration
#

def load_devices():

    with open(DEVICES_CONFIG, "r") as f:
        return json.load(f)


def save_devices(data):

    with open(DEVICES_CONFIG, "w") as f:
        json.dump(data, f, indent=4)


def get_devices():

    data = load_devices()

    return data.get("devices", [])


def add_device(name, ip, ping=True, snmp=False):

    data = load_devices()

    validate_ip(ip)

    customer = load_customer()

    gateway = customer["network"]["gateway"]

    devices = data.setdefault("devices", [])

    if ip == gateway:

        raise Exception(
            "That IP address is already monitored as the Gateway."
        )

    for existing in devices:

        if existing["ip"] == ip:

            raise Exception(
                f"IP address {ip} is already monitored."
            )

        if existing["name"].lower() == name.lower():

            raise Exception(
                f'Device name "{name}" already exists.'
            )

    next_id = 1

    if devices:
        next_id = max(device["id"] for device in devices) + 1

    device = {
        "id": next_id,
        "name": name,
        "ip": ip,
        "checks": {
            "ping": ping,
            "snmp": snmp
        }
    }

    devices.append(device)

    save_devices(data)

    return device


def update_device(device_id, name, ip, ping, snmp):

    data = load_devices()

    for device in data["devices"]:

        if device["id"] == device_id:

            device["name"] = name
            device["ip"] = ip
            device["checks"]["ping"] = ping
            device["checks"]["snmp"] = snmp

            save_devices(data)

            return device

    raise Exception("Device not found")


def remove_device(device_id):

    data = load_devices()

    devices = data["devices"]

    for device in devices:

        if device["id"] == device_id:

            devices.remove(device)

            save_devices(data)

            return device

    raise Exception("Device not found")


#
# Settings
#

def load_settings():

    with open(SETTINGS_CONFIG, "r") as f:
        return json.load(f)


#
# Combined configuration
#

def load():

    return {
        "customer": load_customer(),
        "devices": load_devices(),
        "settings": load_settings()
    }
