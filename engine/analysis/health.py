#!/usr/bin/env python3

def calculate_health(report):

    if report["major_outages"]:

        report["health"] = "POOR"
        return

    if not report["device_counter"]:
        return

    highest = report["device_counter"].most_common(1)[0][1]

    if highest >= 10:

        report["health"] = "FAIR"

    elif highest >= 5:

        report["health"] = "GOOD"

    else:

        report["health"] = "EXCELLENT"