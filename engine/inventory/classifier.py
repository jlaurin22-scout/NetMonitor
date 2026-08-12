#!/usr/bin/env python3

from inventory import fingerprints

def enrich(device):

    hostname = device.hostname.lower()
    vendor = device.vendor.lower()
    ports = set(device.ports)

    #
    # SNMP description (highest priority)
    #
    description = ""

    if hasattr(device, "description") and device.description:
        description = device.description.lower()

    if "vmware esxi" in description:
        device.device_type = "Hypervisor"
        return

    if "ts-" in description or "ts-x" in description:
        device.device_type = "NAS"
        return

    if "synology" in description:
        device.device_type = "NAS"
        return

    if "epson" in description:
        device.device_type = "Printer"
        return

    if "opnsense" in description:
        device.device_type = "Firewall"
        return

    #
    # Fingerprints
    #
    server = device.http_server.lower()
    title = device.http_title.lower()

    values = {

        "vendor": vendor,
        "hostname": hostname,
        "http_server": server,
        "http_title": title,
        "description": description,

    }

    for fingerprint in fingerprints.FINGERPRINTS:

        matched = True

        for key, value in fingerprint.items():

            if key == "type":
                continue

            if value not in values.get(key, ""):

                matched = False
                break

        if matched:

            device.device_type = fingerprint["type"]
            return

    #
    # Vendor based
    #

    if "qnap" in vendor:
        device.device_type = "NAS"
        return

    if vendor == "ubiquiti":
        device.device_type = "Access Point"
        return

    if "vmware" in vendor:
        device.device_type = "Virtual Machine"
        return

    if "avm" in vendor:
        device.device_type = "Router"
        return

    if "devolo" in vendor:
        device.device_type = "Powerline"
        return

    if "d-link" in vendor:
        device.device_type = "Switch"
        return

    if "asus" in vendor and hostname.startswith("wks"):
        device.device_type = "Windows PC"
        return

    if "intel" in vendor and hostname.startswith("miner"):
        device.device_type = "Linux Miner"
        return

    #
    # Port based
    #

    if 515 in ports or 9100 in ports:
        device.device_type = "Printer"
        return

    if 445 in ports and 3389 in ports:
        device.device_type = "Windows PC"
        return

    if 445 in ports and 631 in ports:
        device.device_type = "NAS"
        return

    if 22 in ports and 80 in ports:
        device.device_type = "Linux"
        return

    if 22 in ports:
        device.device_type = "Linux"
        return

    if 80 in ports or 443 in ports:
        device.device_type = "Web Device"
        return

    device.device_type = "Unknown"
