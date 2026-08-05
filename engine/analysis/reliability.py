#!/usr/bin/env python3


def calculate_reliability(report):

    report["device_reliability"] = []

    if not report["device_counter"]:
        return

    highest = max(report["device_counter"].values())

    for device, outages in report["device_counter"].most_common():

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

            "score": score,

            "health": health

        })