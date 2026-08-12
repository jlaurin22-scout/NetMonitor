#!/usr/bin/env python3

from engine import config


def add_monitored_device(
    name,
    ip,
    ping=True,
    snmp=False
):

    config.add_device(
        name=name,
        ip=ip,
        ping=ping,
        snmp=snmp
    )