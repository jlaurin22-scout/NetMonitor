#!/usr/bin/env python3

import os

import ui

from engine import analyzer
from engine.customer_report import generate_customer_report


def customer_report():

    ui.banner("Customer Report")

    print()
    print("Generating customer network analysis report...")
    print()

    report = analyzer.analyze()

    output_path = generate_customer_report(
        report
    )

    print()
    ui.success(
        "Customer report generated successfully."
    )

    print()
    print(
        f"Report : {output_path}"
    )

    print()
    print(
        "The report contains the network availability "
        "and device events recorded during the analysis period."
    )

    print()

    input(
        "Press Enter to continue..."
    )