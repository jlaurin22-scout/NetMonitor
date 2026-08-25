#!/usr/bin/env python3

import json
import ipaddress
import os


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


def load_customer():

    if not os.path.exists(CUSTOMER_CONFIG):

        return {
            "customer": "",
            "address": "",
            "networks": [],
            "tailscale": True
        }

    with open(CUSTOMER_CONFIG, "r") as f:

        data = json.load(f)

    if "networks" not in data:

        data["networks"] = [
            {
                "id": 1,
                "name": "Primary",
                "interface": data["network"]["interface"],
                "ip": data["network"]["ip"],
                "prefix": data["network"]["prefix"],
                "gateway": data["network"]["gateway"],
                "gateway_name": data["network"].get(
                    "gateway_name",
                    "Gateway"
                ),
                "dns": data["network"]["dns"]
            }
        ]

    return data


def save_customer(data):

    with open(CUSTOMER_CONFIG, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )


def update_customer(customer, address):

    data = load_customer()

    data["customer"] = customer
    data["address"] = address

    save_customer(data)


#
# Device Configuration
#

def load_devices():

    if not os.path.exists(DEVICES_CONFIG):

        data = {
            "devices": []
        }

        save_devices(data)

        return data

    with open(DEVICES_CONFIG, "r") as f:

        return json.load(f)


def save_devices(data):

    with open(DEVICES_CONFIG, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )


def get_device_monitoring_mode(device):

    monitoring = device.get(
        "monitoring",
        {}
    )

    mode = monitoring.get(
        "mode",
        "normal"
    )

    if mode not in (
        "normal",
        "standby",
        "conditional"
    ):

        return "normal"

    return mode


def set_device_monitoring_mode(
    device,
    mode
):

    if mode not in (
        "normal",
        "standby",
        "conditional"
    ):

        raise Exception(
            f"Invalid monitoring mode: {mode}"
        )

    device["monitoring"] = {
        "mode": mode
    }


def get_devices():

    data = load_devices()

    devices = data.get(
        "devices",
        []
    )

    #
    # Future-proof:
    # Every device belongs to Network 1 until
    # multi-network support is implemented.
    #
    for device in devices:

        device.setdefault(
            "network_id",
            1
        )

        #
        # Every existing device defaults to normal
        # monitoring if no policy has been configured.
        #
        if "monitoring" not in device:

            device["monitoring"] = {
                "mode": "normal"
            }

        else:

            device["monitoring"].setdefault(
                "mode",
                "normal"
            )

    return devices


def add_device(
    name,
    ip,
    ping=True,
    snmp=False,
    network_id=1,
    monitoring_mode="normal"
):

    data = load_devices()

    validate_ip(ip)

    customer = load_customer()

    network = None

    for item in customer["networks"]:

        if item["id"] == network_id:

            network = item

            break

    if network is None:

        raise Exception(
            "Invalid network."
        )

    if monitoring_mode not in (
        "normal",
        "standby",
        "conditional"
    ):

        raise Exception(
            f"Invalid monitoring mode: {monitoring_mode}"
        )

    gateway = network["gateway"]

    devices = data.setdefault(
        "devices",
        []
    )

    if ip == gateway:

        raise Exception(
            "That IP address is already monitored as the Gateway."
        )

    for existing in devices:

        if (
            existing.get("network_id", 1)
            == network_id
            and
            existing["ip"] == ip
        ):

            raise Exception(
                f"IP address {ip} is already monitored."
            )

        if (
            existing.get("network_id", 1)
            == network_id
            and
            existing["name"].lower()
            == name.lower()
        ):

            raise Exception(
                f'Device name "{name}" already exists.'
            )

    next_id = 1

    if devices:

        next_id = max(
            device["id"]
            for device in devices
        ) + 1

    device = {
        "id": next_id,
        "network_id": network_id,
        "name": name,
        "ip": ip,
        "checks": {
            "ping": ping,
            "snmp": snmp
        },
        "monitoring": {
            "mode": monitoring_mode
        }
    }

    devices.append(device)

    save_devices(data)

    return device


def update_device(
    device_id,
    name,
    ip,
    ping,
    snmp,
    network_id=None,
    monitoring_mode=None
):

    data = load_devices()

    for device in data["devices"]:

        if device["id"] == device_id:

            device["name"] = name
            device["ip"] = ip
            device["checks"]["ping"] = ping
            device["checks"]["snmp"] = snmp

            if network_id is not None:

                device["network_id"] = network_id

            elif "network_id" not in device:

                device["network_id"] = 1

            if monitoring_mode is not None:

                set_device_monitoring_mode(
                    device,
                    monitoring_mode
                )

            elif "monitoring" not in device:

                device["monitoring"] = {
                    "mode": "normal"
                }

            save_devices(data)

            return device

    raise Exception("Device not found")


def remove_device(device_id):

    data = load_devices()

    devices = data["devices"]

    for device in devices:

        if device["id"] == device_id:

            removed = device.copy()

            devices.remove(device)

            save_devices(data)

            return removed

    raise Exception("Device not found")


#
# Settings
#

def load_settings():

    if not os.path.exists(SETTINGS_CONFIG):

        data = {
            "monitor": {
                "gateway_interval": 30,
                "internet_interval": 30,
                "dns_interval": 30,
                "device_interval": 60
            },
            "internet": {
                "targets": [
                    "1.1.1.1",
                    "8.8.8.8"
                ]
            },
            "dns": {
                "server": "1.1.1.1",
                "lookup": "google.com"
            },
            "ntfy": {
                "enabled": False,
                "server": "https://ntfy.sh",
                "topic": "",
                "token": "",
                "name": ""
            }
        }

        save_settings(data)

        return data

    with open(SETTINGS_CONFIG, "r") as f:

        data = json.load(f)

    if "ntfy" not in data:

        data["ntfy"] = {
            "enabled": False,
            "server": "https://ntfy.sh",
            "topic": "",
            "token": "",
            "name": ""
        }

        save_settings(data)

    return data


def save_settings(data):

    with open(SETTINGS_CONFIG, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )


#
# Combined configuration
#

def load():

    return {
        "customer": load_customer(),
        "devices": load_devices(),
        "settings": load_settings()
    }


def get_networks():

    customer = load_customer()

    return customer.get(
        "networks",
        []
    )


def add_network(
    name,
    interface,
    ip,
    prefix,
    gateway,
    gateway_name,
    dns
):

    customer = load_customer()

    networks = customer.setdefault(
        "networks",
        []
    )

    next_id = 1

    if networks:

        next_id = max(
            network["id"]
            for network in networks
        ) + 1

    for network in networks:

        if network["name"].lower() == name.lower():

            raise Exception(
                f'Network "{name}" already exists.'
            )

        if network["interface"] == interface:

            raise Exception(
                f'Interface "{interface}" is already configured.'
            )

    networks.append(
        {
            "id": next_id,
            "name": name,
            "interface": interface,
            "ip": ip,
            "prefix": prefix,
            "gateway": gateway,
            "gateway_name": gateway_name,
            "dns": dns
        }
    )

    save_customer(customer)

    return next_id


def get_network(network_id):

    networks = get_networks()

    for network in networks:

        if network["id"] == network_id:

            return network

    raise Exception("Network not found")


def update_network(
    network_id,
    name,
    interface,
    ip,
    prefix,
    gateway,
    gateway_name,
    dns
):

    customer = load_customer()

    for network in customer["networks"]:

        if network["id"] == network_id:

            network["name"] = name
            network["interface"] = interface
            network["ip"] = ip
            network["prefix"] = prefix
            network["gateway"] = gateway
            network["gateway_name"] = gateway_name
            network["dns"] = dns

            save_customer(customer)

            return network

    raise Exception("Network not found")


def remove_network(network_id):

    customer = load_customer()

    networks = customer["networks"]

    if len(networks) == 1:

        raise Exception(
            "At least one network must exist."
        )

    for network in networks:

        if network["id"] == network_id:

            removed = network.copy()

            networks.remove(network)

            save_customer(customer)

            return removed

    raise Exception("Network not found")