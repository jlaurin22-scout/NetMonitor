#!/usr/bin/env python3


def build_findings(report):

    #
    # DEVICE findings
    #

    for device, count in report["device_counter"].most_common():

        if count >= 10:

            priority = "HIGH"
            confidence = 95

        elif count >= 5:

            priority = "MEDIUM"
            confidence = 80

        else:

            continue

        report["findings"].append({

            "type": "DEVICE",

            "priority": priority,

            "confidence": confidence,

            "score": count,

            "title": "Repeated device instability",

            "device": device,

            "count": count,

            "evidence": [
                f"{count} outages detected",
                "No simultaneous failures detected",
                "Device recovered after each outage"
            ],

            "cause": "Problem appears isolated to this device.",

            "action": "Inspect network cable, PoE and switch port."

        })

    #
    # Aggregate network infrastructure incidents.
    #

    network_events = {}

    for event in report.get(
        "infrastructure_events",
        []
    ):

        for network in event.get(
            "networks",
            []
        ):

            if network not in network_events:

                network_events[network] = {
                    "count": 0,
                    "objects": set()
                }

            network_events[network]["count"] += 1

            network_events[network]["objects"].update(
                event.get(
                    "objects",
                    []
                )
            )

    for network, data in network_events.items():

        count = data["count"]

        objects = sorted(
            data["objects"]
        )

        if count >= 10:

            priority = "HIGH"
            confidence = 95

        elif count >= 5:

            priority = "MEDIUM"
            confidence = 90

        else:

            priority = "LOW"
            confidence = 80

        report["findings"].append({

            "type": "INFRASTRUCTURE",

            "priority": priority,

            "confidence": confidence,

            "score": count * 100,

            "title": (
                f"{network} network instability"
            ),

            "networks": [network],

            "devices": objects,

            "count": count,

            "evidence": [
                f"{count} infrastructure incidents detected",
                f"Affected network: {network}",
                f"Affected checks: {', '.join(objects)}"
            ],

            "cause": (
                f"Repeated failures appear isolated "
                f"to the {network} monitoring path."
            ),

            "action": (
                "Inspect the gateway, network interface "
                "and upstream connectivity."
            )

        })

    #
    # Repeated simultaneous device failures
    #

    for objects, count in report["pair_counter"].items():

        if count < 2:

            continue

        report["findings"].append({

            "type": "INFRASTRUCTURE",

            "priority": "MEDIUM",

            "confidence": 85,

            "score": count + 50,

            "title": "Repeated simultaneous failures",

            "devices": list(objects),

            "count": count,

            "evidence": [
                f"{count} simultaneous failures detected",
                "Same devices affected repeatedly",
                "Failures occurred together"
            ],

            "cause": "Likely shared network infrastructure.",

            "action": "Inspect common switch, PoE switch or uplink."

        })

    #
    # Major outage
    #

    if report["major_outages"]:

        major_event = report["major_events"][0]

        networks = major_event.get(
            "networks",
            []
        )

        objects = major_event.get(
            "objects",
            []
        )

        report["findings"].append({

            "type": "INFRASTRUCTURE",

            "priority": "HIGH",

            "confidence": 98,

            "score": 1000,

            "title": "Major infrastructure outage",

            "networks": networks,

            "devices": objects,

            "count": len(objects),

            "evidence": [
                f"{len(objects)} monitored objects affected",
                "Multiple network paths affected",
                "Represents a site-wide infrastructure event"
            ],

            "cause": (
                "Multiple monitored network paths "
                "became unavailable."
            ),

            "action": (
                "Review gateways, core infrastructure "
                "and Scout availability."
            )

        })