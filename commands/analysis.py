#!/usr/bin/env python3

import ui
from engine import analyzer


def scout_analysis():

    ui.banner("Scout Analysis")

    report = analyzer.analyze()

    print("Executive Summary")
    print("-----------------")
    print()

    print(f"Overall Health : {report['health']}")
    print()

    if report["executive_summary"]["headline"]:

        print("Scout's Assessment")
        print("------------------")
        print()

        print(
            report["executive_summary"]["headline"]
        )

        print()

        for assessment in report[
            "executive_summary"
        ]["assessment"]:

            print(assessment)

        print()

        print("Recommended Investigation Order")
        print("-------------------------------")
        print()

        for number, item in enumerate(
            report["executive_summary"][
                "investigation_order"
            ],
            start=1
        ):

            print(
                f"{number}. {item}"
            )

        print()

    print("Network Statistics")
    print("------------------")
    print()

    print(
        f"Incidents                : "
        f"{report['total_incidents']}"
    )

    print(
        f"Infrastructure Incidents : "
        f"{len(report['infrastructure_events'])}"
    )

    print(
        f"Major Outages            : "
        f"{report['major_outages']}"
    )

    print(
        f"Device Incidents         : "
        f"{report['single_device'] + report['multi_device']}"
    )

    print(
        f"Devices Monitored        : "
        f"{report['devices_monitored']}"
    )

    if report["device_counter"]:

        worst, count = (
            report["device_counter"].most_common(1)[0]
        )

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