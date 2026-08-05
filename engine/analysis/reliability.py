#!/usr/bin/env python3


def calculate_reliability(report):

    report["device_reliability"] = []

    total_downtime = {}

    for incident in report["incidents"]:

        for device in incident["objects"]:

            total_downtime.setdefault(device, 0)

            total_downtime[device] += incident["duration"]

    if not report["device_counter"]:
        return

    highest = max(report["device_counter"].values())

    for device, outages in report["device_counter"].most_common():

        downtime = total_downtime.get(device, 0)

        score = max(
            0,
            round(100 - ((outages / highest) * 60))
        )

        if score >= 99:

            health = "EXCELLENT"

        elif score >= 90:

            health = "GOOD"

        elif score >= 75:

            health = "WARNING"

        else:

            health = "CRITICAL"

        report["device_reliability"].append({

            "device": device,

            "outages": outages,

            "downtime": downtime,

            "score": score,

            "health": health

        })