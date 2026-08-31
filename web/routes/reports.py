#!/usr/bin/env python3

from flask import (
    Blueprint,
    render_template,
    send_file
)

from engine import analyzer
from engine import config
from engine.customer_report import (
    classify_service_outage,
    generate_customer_report
)
from engine.device_report import (
    generate_device_report
)


reports = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


def format_duration(seconds):

    seconds = int(seconds or 0)

    days = seconds // 86400
    seconds %= 86400

    hours = seconds // 3600
    seconds %= 3600

    minutes = seconds // 60
    seconds %= 60

    parts = []

    if days:
        parts.append(
            f"{days}d"
        )

    if hours:
        parts.append(
            f"{hours}h"
        )

    if minutes:
        parts.append(
            f"{minutes}m"
        )

    if seconds or not parts:
        parts.append(
            f"{seconds}s"
        )

    return " ".join(parts)


def format_timestamp(value):

    if not value:
        return "-"

    return value


def service_summary(service_outages):

    summary = {
        "MINOR INTERRUPTION": {
            "count": 0,
            "downtime": 0,
        },
        "SERVICE OUTAGE": {
            "count": 0,
            "downtime": 0,
        },
        "MAJOR SERVICE OUTAGE": {
            "count": 0,
            "downtime": 0,
        },
    }

    for outage in service_outages:

        classification = outage.get(
            "severity",
            "SERVICE OUTAGE"
        )

        classification = {
            "BRIEF INTERRUPTION": "MINOR INTERRUPTION",
            "MINOR INTERRUPTION": "MINOR INTERRUPTION",
            "SERVICE OUTAGE": "SERVICE OUTAGE",
            "MAJOR OUTAGE": "MAJOR SERVICE OUTAGE",
            "MAJOR SERVICE OUTAGE": "MAJOR SERVICE OUTAGE",
        }.get(
            classification,
            "SERVICE OUTAGE"
        )

        duration = int(
            outage.get(
                "duration",
                0
            )
        )

        summary[classification]["count"] += 1

        summary[classification]["downtime"] += duration

    return summary


def build_report():

    report = analyzer.analyze()

    service_outages = report.get(
        "service_outages",
        []
    )

    #
    # Calculate totals here rather than inside
    # the Jinja template. Jinja loop variables
    # do not retain their changed values outside
    # the loop.
    #

    report["total_service_downtime"] = sum(
        int(
            outage.get(
                "duration",
                0
            )
        )
        for outage in service_outages
    )

    report["total_device_downtime"] = sum(
        int(
            device.get(
                "downtime",
                0
            )
        )
        for device in report.get(
            "device_reliability",
            []
        )
    )

    return (
        report,
        service_summary(
            service_outages
        )
    )


@reports.route("/")
def index():

    customer = config.load_customer()

    report, services = build_report()

    return render_template(
        "reports.html",
        customer=customer.get(
            "customer",
            "Unknown"
        ),
        address=customer.get(
            "address",
            ""
        ),
        report=report,
        services=services,
        format_duration=format_duration,
        format_timestamp=format_timestamp,
        classify_service_outage=classify_service_outage,
    )


@reports.route(
    "/download"
)
def download():

    report, services = build_report()

    output_path = generate_customer_report(
        report
    )

    return send_file(
        output_path,
        as_attachment=True,
        download_name=output_path.split("/")[-1],
        mimetype="application/pdf"
    )


@reports.route(
    "/download-device-summary"
)
def download_device_summary():

    report, services = build_report()

    output_path = generate_device_report(
        report
    )

    return send_file(
        output_path,
        as_attachment=True,
        download_name=output_path.split("/")[-1],
        mimetype="application/pdf"
    )