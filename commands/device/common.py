#!/usr/bin/env python3

from engine import config


def add_monitored_device(
    name,
    ip,
    ping=True,
    snmp=False,
    network_id=None
):

    if network_id is None:

        networks = config.get_networks()

        if len(networks) == 1:

            network_id = networks[0]["id"]

        else:

            raise Exception(
                "A network must be selected."
            )

    config.add_device(
        name=name,
        ip=ip,
        ping=ping,
        snmp=snmp,
        network_id=network_id
    )
