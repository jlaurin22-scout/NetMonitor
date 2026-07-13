#!/usr/bin/env python3

"""
NetMonitor SNMP v2c interface.
"""

from pysnmp.hlapi import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    getCmd,
)


def _execute(ip, community, objects, timeout=2, retries=0):

    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget(
            (ip, 161),
            timeout=timeout,
            retries=retries,
        ),
        ContextData(),
        *objects,
    )

    return next(iterator)


def snmp_probe(ip, community="public"):
    """
    Fast probe to determine whether an SNMP agent is available.

    Returns True if the device answers, otherwise False.
    """

    try:

        error_indication, error_status, _, _ = _execute(
            ip,
            community,
            [ObjectType(ObjectIdentity("1.3.6.1.2.1.1.1.0"))],
            timeout=0.25,
            retries=0,
        )

        if error_indication:
            return False

        if error_status:
            return False

        return True

    except Exception:
        return False


def snmp_get(ip, community, oid, timeout=2, retries=0):

    result = snmp_get_many(
        ip,
        community,
        [oid],
        timeout,
        retries,
    )

    return result.get(oid)


def snmp_get_many(ip, community, oids, timeout=2, retries=0):

    try:

        objects = [
            ObjectType(ObjectIdentity(oid))
            for oid in oids
        ]

        error_indication, error_status, _, var_binds = _execute(
            ip,
            community,
            objects,
            timeout,
            retries,
        )

        if error_indication:
            return {}

        if error_status:
            return {}

        results = {}

        for oid, value in var_binds:
            results[str(oid)] = str(value)

        return results

    except Exception:
        return {}
