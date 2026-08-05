from collections import Counter

from database import get_incidents, get_recent_events
from config import get_devices
from analysis.health import calculate_health
from analysis.summary import build_summary

MAJOR_OUTAGE_THRESHOLD = 10

def analyze():

    devices = {}

    for device in get_devices():

        devices[device["name"]] = device["name"]
        devices[device["ip"]] = device["name"]

    incidents = get_incidents()

    report = {
        "health": "EXCELLENT",
        "devices_monitored": len(get_devices()),
        "total_incidents": len(incidents),
        "single_device": 0,
        "multi_device": 0,
        "major_outages": 0,
        "device_counter": Counter(),
        "pair_counter": Counter(),
        "major_events": [],
        "findings": [],
        "top_findings": [],
        "executive_summary": {
            "headline": "",
            "assessment": [],
            "investigation_order": []
        }
    }

    for incident in incidents:

        objects = sorted(
            devices.get(obj, obj)
            for obj in incident["objects"]
        )

        if len(objects) == 1:

            report["single_device"] += 1
            report["device_counter"][objects[0]] += 1

        elif len(objects) >= MAJOR_OUTAGE_THRESHOLD:

            report["major_outages"] += 1
            report["major_events"].append(objects)

        else:

            report["multi_device"] += 1

            for obj in objects:
                report["device_counter"][obj] += 1

            report["pair_counter"][tuple(objects)] += 1

    #
    # Overall Health
    #

    calculate_health(report)
    
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

    build_summary(report)
    
    return report
