#!/usr/bin/env python3

"""
NetMonitor SNMP Enrichment Plugin
"""

from inventory.snmp.mib import SYSTEM_OIDS
from inventory.snmp.v2 import snmp_probe, snmp_get_many

DEFAULT_COMMUNITY = "public"


def enrich(device):

    device.snmp = False

    #
    # Fast probe first.
    #
    if not snmp_probe(device.ip, DEFAULT_COMMUNITY):
        return

    values = snmp_get_many(
        device.ip,
        DEFAULT_COMMUNITY,
        list(SYSTEM_OIDS.values())
    )

    if not values:
        return

    device.snmp = True

    description = values.get(SYSTEM_OIDS["description"], "")
    hostname = values.get(SYSTEM_OIDS["name"], "")
    uptime = values.get(SYSTEM_OIDS["uptime"], "")
    contact = values.get(SYSTEM_OIDS["contact"], "")
    location = values.get(SYSTEM_OIDS["location"], "")

    if description:
        device.description = description

    if hostname and not device.hostname:
        device.hostname = hostname

    if uptime:
        device.uptime = uptime

    if contact and contact != '""':
        device.contact = contact

    if location and location != '""':
        device.location = location
