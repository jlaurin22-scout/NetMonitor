#!/usr/bin/env python3

def build_summary(report):

    report["executive_summary"] = {
        "headline": "",
        "assessment": [],
        "investigation_order": []
    }

    if not report["findings"]:
        return

    first = report["findings"][0]

    if first["type"] == "INFRASTRUCTURE":

        report["executive_summary"]["headline"] = (
            "Site-wide infrastructure outage detected."
        )

        report["executive_summary"]["assessment"] = [

            (
                f"{first['count']} monitored devices became "
                "unreachable."
            ),

            (
                "The outage is consistent with a gateway, "
                "core switch or power failure."
            )

        ]

    elif first["type"] == "DEVICE":

        report["executive_summary"]["headline"] = (
            f"{first['device']} requires immediate attention."
        )

        report["executive_summary"]["assessment"] = [

            (
                f"{first['count']} outage/recovery cycles "
                "were recorded."
            ),

            (
                "No evidence currently indicates a wider "
                "network problem."
            )

        ]

    for finding in report["top_findings"]:

        if "device" in finding:

            report["executive_summary"][
                "investigation_order"
            ].append(
                f"Inspect {finding['device']}"
            )

        else:

            report["executive_summary"][
                "investigation_order"
            ].append(
                "Investigate network infrastructure"
            )