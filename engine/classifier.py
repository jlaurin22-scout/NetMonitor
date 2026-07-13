#!/usr/bin/env python3

from constants import STATE_DOWN


def classify(status):

    gateway = None
    internet = None
    dns = None

    failed_devices = []

    for name, info in status.items():

        job_type = info["type"]
        state = info["state"]

        if job_type == "gateway":
            gateway = state

        elif job_type == "internet":
            internet = state

        elif job_type == "dns":
            dns = state

        elif job_type == "device" and state == STATE_DOWN:
            failed_devices.append(info)

    #
    # Router Failure
    #
    if gateway == STATE_DOWN:
        return {
            "classification": "Router Failure",
            "confidence": 100
        }

    #
    # ISP Failure
    #
    if gateway != STATE_DOWN and internet == STATE_DOWN:
        return {
            "classification": "ISP Failure",
            "confidence": 95
        }

    #
    # DNS Failure
    #
    if internet != STATE_DOWN and dns == STATE_DOWN:
        return {
            "classification": "DNS Failure",
            "confidence": 95
        }

    #
    # Device-specific failures
    #
    if len(failed_devices) == 1:

        device_type = failed_devices[0]["device_type"].lower()

        if device_type == "radio":
            return {
                "classification": "Internet Radio Failure",
                "confidence": 99
            }

        if device_type == "nas":
            return {
                "classification": "NAS Failure",
                "confidence": 99
            }

        if device_type == "switch":
            return {
                "classification": "Network Switch Failure",
                "confidence": 95
            }

        return {
            "classification": "Single Device Failure",
            "confidence": 98
        }

    if len(failed_devices) > 1:
        return {
            "classification": "Multiple Device Failure",
            "confidence": 98
        }

    return {
        "classification": "Normal",
        "confidence": 100
    }
