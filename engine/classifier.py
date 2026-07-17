#!/usr/bin/env python3

from constants import STATE_DOWN


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

    #
    # Gateway unreachable
    #
    if gateway == STATE_DOWN:
        return {
            "classification": "Gateway Unreachable",
            "confidence": 100
        }

    #
    # Internet unreachable
    #
    if gateway != STATE_DOWN and internet == STATE_DOWN:
        return {
            "classification": "Internet Unreachable",
            "confidence": 100
        }

    #
    # DNS failure
    #
    if internet != STATE_DOWN and dns == STATE_DOWN:
        return {
            "classification": "DNS Failure",
            "confidence": 100
        }

    #
    # Device failures
    #
    if failed_devices == 1:
        return {
            "classification": "Single Device Failure",
            "confidence": 100
        }

    if failed_devices > 1:
        return {
            "classification": "Multiple Device Failure",
            "confidence": 100
        }

    return {
        "classification": "Normal",
        "confidence": 100
    }
