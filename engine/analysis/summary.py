#!/usr/bin/env python3


def build_summary(report):

    report["executive_summary"] = {
        "headline": "",
        "assessment": [],
        "investigation_order": []
    }

    if not report["findings"]:

        report["executive_summary"]["headline"] = (
            "No significant network problems detected."
        )

        report["executive_summary"]["assessment"] = [
            "All monitored network paths are currently operational."
        ]

        return

    infrastructure_findings = [
        finding
        for finding in report["findings"]
        if finding["type"] == "INFRASTRUCTURE"
    ]

    device_findings = [
        finding
        for finding in report["findings"]
        if finding["type"] == "DEVICE"
    ]

    #
    # Multiple networks affected.
    #

    if report["major_outages"]:

        report["executive_summary"]["headline"] = (
            "Site-wide infrastructure outage detected."
        )

        report["executive_summary"]["assessment"] = [

            (
                f"{report['major_outages']} major "
                "infrastructure outage(s) detected."
            ),

            (
                "Multiple monitored network paths "
                "were affected."
            )

        ]

    #
    # Network-specific infrastructure problems.
    #

    elif infrastructure_findings:

        report["executive_summary"]["headline"] = (
            "Network infrastructure instability detected."
        )

        assessment = []

        for finding in infrastructure_findings:

            networks = finding.get(
                "networks",
                []
            )

            count = finding.get(
                "count",
                0
            )

            if len(networks) == 1:

                network = networks[0]

                assessment.append(
                    (
                        f"{network}: {count} "
                        "infrastructure incident(s) detected."
                    )
                )

            else:

                assessment.append(
                    (
                        f"{count} infrastructure "
                        "incident(s) detected."
                    )
                )

        report["executive_summary"]["assessment"] = assessment

    #
    # Device-only problems.
    #

    elif device_findings:

        first = device_findings[0]

        report["executive_summary"]["headline"] = (
            f"{first['device']} requires attention."
        )

        report["executive_summary"]["assessment"] = [

            (
                f"{first['count']} outage/recovery "
                "cycles were recorded."
            ),

            (
                "No evidence currently indicates "
                "a wider network problem."
            )

        ]

    #
    # Investigation order.
    #

    for finding in report["top_findings"]:

        networks = finding.get(
            "networks",
            []
        )

        if networks:

            for network in networks:

                report["executive_summary"][
                    "investigation_order"
                ].append(
                    f"Investigate {network} network path"
                )

        elif "device" in finding:

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