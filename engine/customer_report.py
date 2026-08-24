#!/usr/bin/env python3

import json
import os
import sqlite3

from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


DB = "/var/lib/netmonitor/netmonitor.db"
CONFIG = "/etc/netmonitor/netmonitor.json"
REPORT_DIR = "/var/lib/netmonitor/reports"


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
        parts.append(f"{days}d")

    if hours:
        parts.append(f"{hours}h")

    if minutes:
        parts.append(f"{minutes}m")

    if seconds or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def format_timestamp(value):

    if not value:
        return "-"

    try:

        timestamp = datetime.strptime(
            value,
            "%Y-%m-%d %H:%M:%S"
        )

        return timestamp.strftime(
            "%d.%m.%Y %H:%M:%S"
        )

    except ValueError:

        return value


def get_analysis_period():

    conn = sqlite3.connect(DB)

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            MIN(timestamp),
            MAX(timestamp)
        FROM events
        """
    )

    row = cur.fetchone()

    conn.close()

    if not row or not row[0]:

        return None, None

    return row[0], row[1]


def load_config():

    try:

        with open(
            CONFIG,
            "r",
            encoding="utf-8"
        ) as handle:

            return json.load(handle)

    except (
        OSError,
        json.JSONDecodeError
    ):

        return {}


def build_styles():

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
            spaceAfter=4,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1f4e79"),
            spaceBefore=12,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SubHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            spaceBefore=6,
            spaceAfter=5,
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            spaceAfter=4,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            spaceAfter=3,
        )
    )

    return styles


def make_table(
    data,
    widths=None,
    header=True,
    font_size=8,
):

    table_data = []

    for row_index, row in enumerate(data):

        table_row = []

        for cell in row:

            if isinstance(cell, str):

                if header and row_index == 0:

                    style = ParagraphStyle(
                        "TableHeader",
                        fontName="Helvetica-Bold",
                        fontSize=font_size,
                        leading=font_size + 2,
                        textColor=colors.white,
                    )

                else:

                    style = ParagraphStyle(
                        "TableCell",
                        fontName="Helvetica",
                        fontSize=font_size,
                        leading=font_size + 2,
                    )

                table_row.append(
                    Paragraph(
                        cell.replace(
                            "\n",
                            "<br/>"
                        ),
                        style
                    )
                )

            else:

                table_row.append(cell)

        table_data.append(table_row)

    table = Table(
        table_data,
        colWidths=widths,
        repeatRows=1 if header else 0,
        hAlign="LEFT",
    )

    commands = [
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP",
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.35,
            colors.HexColor("#cccccc"),
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            5,
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            5,
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            5,
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            5,
        ),
    ]

    if header:

        commands.extend(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f4e79"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
            ]
        )

    for row in range(
        1 if header else 0,
        len(table_data)
    ):

        if row % 2 == 0:

            commands.append(
                (
                    "BACKGROUND",
                    (0, row),
                    (-1, row),
                    colors.HexColor("#f5f7fa"),
                )
            )

    table.setStyle(
        TableStyle(commands)
    )

    return table

def add_page_number(canvas, document):

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.setFillColor(
        colors.HexColor("#777777")
    )

    canvas.drawString(
        20 * mm,
        12 * mm,
        "Scout Network Monitor"
    )

    canvas.drawRightString(
        A4[0] - (20 * mm),
        12 * mm,
        f"Page {document.page}"
    )

    canvas.restoreState()


def service_summary(service_outages):

    summary = {
        "BRIEF INTERRUPTION": {
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
        "MAJOR OUTAGE": {
            "count": 0,
            "downtime": 0,
        },
    }

    for outage in service_outages:

        severity = outage.get(
            "severity",
            "SERVICE OUTAGE"
        )

        if severity not in summary:

            summary[severity] = {
                "count": 0,
                "downtime": 0,
            }

        summary[severity]["count"] += 1

        summary[severity]["downtime"] += int(
            outage.get(
                "duration",
                0
            )
        )

    return summary


def generate_customer_report(
    report,
    output_path=None
):

    config = load_config()

    customer = config.get(
        "customer",
        "Customer"
    )

    address = config.get(
        "address",
        ""
    )

    start, end = get_analysis_period()

    if output_path is None:

        if start:

            try:

                start_dt = datetime.strptime(
                    start,
                    "%Y-%m-%d %H:%M:%S"
                )

                date_part = start_dt.strftime(
                    "%Y-%m-%d"
                )

            except ValueError:

                date_part = "unknown"

        else:

            date_part = "unknown"

        output_path = os.path.join(
            REPORT_DIR,
            f"Network_Analysis_Report_{date_part}.pdf"
        )

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:

        os.makedirs(
            output_directory,
            exist_ok=True
        )

    styles = build_styles()

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Network Analysis Report",
        author="Scout Network Monitor",
    )

    story = []

    #
    # Report header
    #

    story.append(
        Spacer(1, 8 * mm)
    )

    story.append(
        Paragraph(
            "NETWORK ANALYSIS REPORT",
            styles["ReportTitle"]
        )
    )

    story.append(
        Paragraph(
            "Scout Network Monitor",
            styles["ReportSubtitle"]
        )
    )

    story.append(
        Spacer(1, 7 * mm)
    )

    customer_data = [
        [
            Paragraph(
                "<b>Customer</b>",
                styles["BodySmall"]
            ),
            Paragraph(
                str(customer),
                styles["BodySmall"]
            ),
        ],
        [
            Paragraph(
                "<b>Site / Address</b>",
                styles["BodySmall"]
            ),
            Paragraph(
                str(address) if address else "-",
                styles["BodySmall"]
            ),
        ],
        [
            Paragraph(
                "<b>Analysis Start</b>",
                styles["BodySmall"]
            ),
            Paragraph(
                format_timestamp(start),
                styles["BodySmall"]
            ),
        ],
        [
            Paragraph(
                "<b>Analysis End</b>",
                styles["BodySmall"]
            ),
            Paragraph(
                format_timestamp(end),
                styles["BodySmall"]
            ),
        ],
    ]

    story.append(
        Table(
            customer_data,
            colWidths=[
                42 * mm,
                125 * mm
            ],
            style=TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        colors.HexColor("#cccccc"),
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor("#f0f3f6"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )
    )

    #
    # Executive Summary
    #

    story.append(
        Paragraph(
            "Executive Summary",
            styles["SectionHeading"]
        )
    )

    total_incidents = report.get(
        "total_incidents",
        0
    )

    service_outages = report.get(
        "service_outages",
        []
    )

    service_counts = service_summary(
        service_outages
    )

    device_incidents = (
        report.get(
            "single_device",
            0
        )
        +
        report.get(
            "multi_device",
            0
        )
    )

    major_service_outages = (
        service_counts[
            "MAJOR SERVICE OUTAGE"
        ]["count"]
    )

    major_outages = (
        service_counts[
            "MAJOR OUTAGE"
        ]["count"]
    )

    if (
        major_service_outages
        or
        major_outages
    ):

        headline = (
            "Significant service interruptions "
            "were recorded during the analysis period."
        )

    elif service_outages:

        headline = (
            "Service interruptions were recorded "
            "during the analysis period."
        )

    elif device_incidents:

        headline = (
            "The network services remained available, "
            "with device incidents recorded."
        )

    else:

        headline = (
            "No service or device incidents were "
            "recorded during the analysis period."
        )

    story.append(
        Paragraph(
            f"<b>{headline}</b>",
            styles["BodySmall"]
        )
    )

    story.append(
        Paragraph(
            (
                f"Watchdog recorded {total_incidents} "
                f"incident period(s) during the "
                f"analysis period."
            ),
            styles["BodySmall"]
        )
    )

    story.append(
        Paragraph(
            (
                f"{len(service_outages)} network service "
                f"outage event(s) and {device_incidents} "
                f"device incident(s) were recorded."
            ),
            styles["BodySmall"]
        )
    )

    #
    # Service Availability
    #

    story.append(
        Paragraph(
            "Service Availability",
            styles["SectionHeading"]
        )
    )

    service_data = [
        [
            "Classification",
            "Events",
            "Total Downtime",
        ],
        [
            "Brief Interruption",
            str(
                service_counts[
                    "BRIEF INTERRUPTION"
                ]["count"]
            ),
            format_duration(
                service_counts[
                    "BRIEF INTERRUPTION"
                ]["downtime"]
            ),
        ],
        [
            "Service Outage",
            str(
                service_counts[
                    "SERVICE OUTAGE"
                ]["count"]
            ),
            format_duration(
                service_counts[
                    "SERVICE OUTAGE"
                ]["downtime"]
            ),
        ],
        [
            "Major Service Outage",
            str(
                service_counts[
                    "MAJOR SERVICE OUTAGE"
                ]["count"]
            ),
            format_duration(
                service_counts[
                    "MAJOR SERVICE OUTAGE"
                ]["downtime"]
            ),
        ],
        [
            "Major Outage",
            str(
                service_counts[
                    "MAJOR OUTAGE"
                ]["count"]
            ),
            format_duration(
                service_counts[
                    "MAJOR OUTAGE"
                ]["downtime"]
            ),
        ],
    ]

    story.append(
        make_table(
            service_data,
            widths=[
                82 * mm,
                35 * mm,
                50 * mm,
            ]
        )
    )

    story.append(
        Spacer(1, 2 * mm)
    )

    story.append(
        Paragraph(
            (
                "<b>Classification:</b> Brief interruptions "
                "are events shorter than 30 seconds. Service "
                "outages last from 30 seconds through 5 minutes. "
                "Major service outages exceed 5 minutes. A "
                "major outage is recorded when multiple critical "
                "network services fail during the same incident."
            ),
            styles["Small"]
        )
    )

    #
    # Device Reliability
    #

    reliability = report.get(
        "device_reliability",
        []
    )

    if reliability:

        story.append(
            Paragraph(
                "Device Reliability",
                styles["SectionHeading"]
            )
        )

        reliability_data = [
            [
                "Device",
                "Reliability",
                "Health",
                "Outages",
                "Downtime",
            ]
        ]

        for device in reliability:

            reliability_data.append(
                [
                    str(
                        device.get(
                            "device",
                            "-"
                        )
                    ),
                    f"{device.get('score', 0)}%",
                    str(
                        device.get(
                            "health",
                            "-"
                        )
                    ),
                    str(
                        device.get(
                            "outages",
                            0
                        )
                    ),
                    format_duration(
                        device.get(
                            "downtime",
                            0
                        )
                    ),
                ]
            )

        story.append(
            make_table(
                reliability_data,
                widths=[
                    65 * mm,
                    25 * mm,
                    28 * mm,
                    22 * mm,
                    27 * mm,
                ]
            )
        )

    #
    # Service Outage History
    #

    if service_outages:

        story.append(
            Paragraph(
                "Service Outage History",
                styles["SectionHeading"]
            )
        )

        for number, outage in enumerate(
            service_outages,
            start=1
        ):

            networks = outage.get(
                "networks",
                []
            )

            objects = outage.get(
                "objects",
                []
            )

            severity = outage.get(
                "severity",
                "SERVICE OUTAGE"
            )

            story.append(
                Paragraph(
                    (
                        f"<b>Event {number} — "
                        f"{severity}</b>"
                    ),
                    styles["SubHeading"]
                )
            )

            outage_data = [
                [
                    "Start",
                    format_timestamp(
                        outage.get(
                            "start"
                        )
                    ),
                ],
                [
                    "End",
                    format_timestamp(
                        outage.get(
                            "end"
                        )
                    ),
                ],
                [
                    "Duration",
                    format_duration(
                        outage.get(
                            "duration",
                            0
                        )
                    ),
                ],
                [
                    "Network",
                    ", ".join(
                        networks
                    ) if networks else "-",
                ],
                [
                    "Affected Services",
                    ", ".join(
                        objects
                    ) if objects else "-",
                ],
            ]

            story.append(
                make_table(
                    outage_data,
                    widths=[
                        42 * mm,
                        125 * mm,
                    ],
                    header=False,
                )
            )

            story.append(
                Spacer(1, 3 * mm)
            )

    #
    # Device Incident History
    #

    device_incident_events = []

    for incident in report.get(
        "incidents",
        []
    ):

        object_types = incident.get(
            "object_types",
            {}
        )

        device_objects = [
            obj
            for obj in incident.get(
                "objects",
                []
            )
            if object_types.get(obj) == "device"
        ]

        if device_objects:

            device_incident_events.append(
                (
                    incident,
                    sorted(
                        device_objects
                    )
                )
            )

    if device_incident_events:

        story.append(
            Paragraph(
                "Device Incident History",
                styles["SectionHeading"]
            )
        )

        for number, item in enumerate(
            device_incident_events,
            start=1
        ):

            incident, devices = item

            incident_data = [
                [
                    "Start",
                    format_timestamp(
                        incident.get(
                            "start"
                        )
                    ),
                ],
                [
                    "End",
                    format_timestamp(
                        incident.get(
                            "end"
                        )
                    ),
                ],
                [
                    "Duration",
                    format_duration(
                        incident.get(
                            "duration",
                            0
                        )
                    ),
                ],
                [
                    "Network",
                    ", ".join(
                        sorted(
                            incident.get(
                                "networks",
                                []
                            )
                        )
                    ) or "-",
                ],
                [
                    "Affected Device(s)",
                    ", ".join(
                        devices
                    ),
                ],
            ]

            story.append(
                Paragraph(
                    f"<b>Device Event {number}</b>",
                    styles["SubHeading"]
                )
            )

            story.append(
                make_table(
                    incident_data,
                    widths=[
                        42 * mm,
                        125 * mm,
                    ],
                    header=False,
                )
            )

            story.append(
                Spacer(1, 3 * mm)
            )

    #
    # Conclusion
    #

    story.append(
        Paragraph(
            "Conclusion",
            styles["SectionHeading"]
        )
    )

    total_service_downtime = sum(
        int(
            outage.get(
                "duration",
                0
            )
        )
        for outage in service_outages
    )

    total_device_downtime = sum(
        int(
            device.get(
                "downtime",
                0
            )
        )
        for device in reliability
    )

    conclusion = (
        f"During the analysis period, Watchdog recorded "
        f"{len(service_outages)} network service outage "
        f"event(s), with a combined recorded service "
        f"downtime of {format_duration(total_service_downtime)}. "
        f"Monitored devices recorded a combined downtime "
        f"of {format_duration(total_device_downtime)}. "
        "This report documents the events observed by the "
        "monitoring system during the analysis period."
    )

    story.append(
        Paragraph(
            conclusion,
            styles["BodySmall"]
        )
    )

    story.append(
        Spacer(1, 4 * mm)
    )

    story.append(
        Paragraph(
            (
                "The classifications and timings in this "
                "report are based on the monitoring checks "
                "configured on the Scout Network Monitor. "
                "They describe observed availability events "
                "and do not establish the physical or technical "
                "root cause of an outage."
            ),
            styles["Small"]
        )
    )

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return output_path