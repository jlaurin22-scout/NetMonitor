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
    # INFRASTRUCTURE findings
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
    # MAJOR OUTAGE
    #

    if report["major_outages"]:

        report["findings"].append({

            "type": "INFRASTRUCTURE",

            "priority": "HIGH",

            "confidence": 98,

            "score": 1000,

            "title": "Major infrastructure outage",

            "devices": report["major_events"][0],

            "count": len(report["major_events"][0]),

            "evidence": [
                f"{len(report['major_events'][0])} monitored devices affected",
                "Large-scale simultaneous outage",
                "Represents network-wide event"
            ],

            "cause": "Large part of the monitored network became unavailable.",

            "action": "Review gateway, core switch and Scout availability."

        })

    report["findings"].sort(
        key=lambda f: f["score"],
        reverse=True
    )

    report["top_findings"] = report["findings"][:3]