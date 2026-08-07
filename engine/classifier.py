#!/usr/bin/env python3

from engine.constants import STATE_DOWN


def classify(status):

    gateway = None
    internet = None
    dns = None

    failed_devices = 0

    for info in status.values():

        job_type = info["type"]
        state = info["state"]

        if job_type == "gateway":
            gateway = state

        elif job_type == "internet":
            internet = state

        elif job_type == "dns":
            dns = state

        elif job_type == "device" and state == STATE_DOWN:
            failed_devices += 1

    return classify_values(
        gateway,
        internet,
        dns,
        failed_devices
    )


def classify_values(
    gateway,
    internet,
    dns,
    failed_devices
):

    #
    # Gateway unreachable
    #

    if gateway == STATE_DOWN:

        return {
            "type": "GATEWAY",
            "classification": "Gateway Unreachable",
            "confidence": 100
        }

    #
    # Internet unreachable
    #

    if gateway != STATE_DOWN and internet == STATE_DOWN:

        return {
            "type": "INTERNET",
            "classification": "Internet Unreachable",
            "confidence": 100
        }

    #
    # DNS failure
    #

    if internet != STATE_DOWN and dns == STATE_DOWN:

        return {
            "type": "DNS",
            "classification": "DNS Failure",
            "confidence": 100
        }

    #
    # Device failures
    #

    if failed_devices == 1:

        return {
            "type": "DEVICE",
            "classification": "Single Device Failure",
            "confidence": 100
        }

    if failed_devices > 1:

        return {
            "type": "INFRASTRUCTURE",
            "classification": "Multiple Device Failure",
            "confidence": 100
        }

    return {
        "type": "NORMAL",
        "classification": "Normal",
        "confidence": 100
    }
