#!/usr/bin/env python3


def rank_findings(report):

    report["findings"].sort(
        key=lambda finding: finding["score"],
        reverse=True
    )

    report["top_findings"] = report["findings"][:3]