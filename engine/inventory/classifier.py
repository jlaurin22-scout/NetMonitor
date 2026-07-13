#!/usr/bin/env python3


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
    # Hostname based
    #

    if "opnsense" in hostname:
        device.device_type = "Firewall"
        return

    if hostname.startswith("srv"):
        device.device_type = "Windows Server"
        return

    if "kamera" in hostname:
        device.device_type = "Camera"
        return

    if "switch" in hostname:
        device.device_type = "Switch"
        return

    if "printer" in hostname:
        device.device_type = "Printer"
        return

    if "devolo" in hostname:
        device.device_type = "Powerline"
        return

    if "net-monitor" in hostname:
        device.device_type = "NetMonitor"
        return

    #
    # Vendor based
    #

    if vendor == "qnap":
        device.device_type = "NAS"
        return

    if vendor == "ubiquiti":
        device.device_type = "Access Point"
        return

    if vendor == "vmware":
        device.device_type = "Virtual Machine"
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
