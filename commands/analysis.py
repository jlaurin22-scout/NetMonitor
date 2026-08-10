#!/usr/bin/env python3

import ui
from engine import analyzer

def scout_analysis():

    banner()

    report = analyzer.analyze()

    print("Scout Analysis")
    print("==============")
    print()

    print("Executive Summary")
    print("-----------------")
    print()

    print(f"Overall Health : {report['health']}")
    print()

    if report["findings"]:

        first = report["findings"][0]

        print("Scout's Assessment")
        print("------------------")
        print()

        if first["type"] == "INFRASTRUCTURE":

            print(
                "Scout detected a site-wide infrastructure outage."
            )

            print()

            print(
                f"{first['count']} monitored devices became "
                "unreachable during the incident."
            )

            print(
                "The event is consistent with a failure of the "
                "gateway, core switch or site power."
            )

        elif first["type"] == "DEVICE":

            print(
                f"Scout identified {first['device']} as the "
                "least reliable monitored device."
            )

            print()

            print(
                f"{first['count']} outage/recovery cycles have "
                "been recorded."
            )

            print(
                "No evidence currently suggests a wider network "
                "problem."
            )

        print()

        print("Recommended Investigation Order")
        print("-------------------------------")
        print()

        for number, finding in enumerate(
            report["top_findings"],
            start=1
        ):

            if "device" in finding:

                print(
                    f"{number}. Inspect {finding['device']}"
                )

            else:

                print(
                    f"{number}. Investigate network infrastructure"
                )

        print()

    print("Network Statistics")
    print("------------------")
    print()

    print(f"Incidents              : {report['total_incidents']}")
    print(f"Infrastructure Outages : {report['major_outages']}")
    print(
        f"Device Incidents       : "
        f"{report['single_device'] + report['multi_device']}"
    )
    print(
        f"Devices Monitored      : "
        f"{report['devices_monitored']}"
    )

    if report["device_counter"]:

        worst, count = report["device_counter"].most_common(1)[0]

        print(
            f"Worst Device           : "
            f"{worst} ({count})"
        )

    print()

    print("Device Reliability")
    print("------------------")
    print()

    if report["device_reliability"]:

        for device in report["device_reliability"]:

            downtime = device["downtime"]

            hours = downtime // 3600
            minutes = (downtime % 3600) // 60
            seconds = downtime % 60

            if hours:

                downtime_text = (
                    f"{hours}h {minutes}m {seconds}s"
                )

            elif minutes:

                downtime_text = (
                    f"{minutes}m {seconds}s"
                )

            else:

                downtime_text = (
                    f"{seconds}s"
                )

            print(
                f"{device['device']:<20} "
                f"{device['score']:>3}%   "
                f"{device['health']}"
            )

            print(
                f"{'':20} "
                f"Outages : {device['outages']}"
            )

            print(
                f"{'':20} "
                f"Downtime: {downtime_text}"
            )

            print()

    else:

        print("No reliability data available.")

    print()
    

