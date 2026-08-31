#!/usr/bin/env python3

import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from engine import config


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


def safe_filename(value):

    value = str(value or "").strip()

    if not value:
        return "Customer"

    invalid = '<>:"/\\|?*'

    value = "".join(
        "_"
        if character in invalid
        else character
        for character in value
    )

    value = " ".join(
        value.split()
    )

    value = value.strip(
        " ."
    )

    return value or "Customer"


def build_styles():

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="DeviceReportTitle",
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
            name="DeviceReportSubtitle",
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
            name="DeviceSectionHeading",
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
            name="DeviceBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            spaceAfter=5,
        )
    )

    styles.add(
        ParagraphStyle(
            name="DeviceSmall",
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
):

    table_data = []

    for row_index, row in enumerate(data):

        table_row = []

        for cell in row:

            if isinstance(cell, str):

                if row_index == 0:

                    style = ParagraphStyle(
                        "DeviceTableHeader",
                        fontName="Helvetica-Bold",
                        fontSize=8,
                        leading=10,
                        textColor=colors.white,
                    )

                else:

                    style = ParagraphStyle(
                        "DeviceTableCell",
                        fontName="Helvetica",
                        fontSize=8,
                        leading=10,
                    )

                table_row.append(
                    Paragraph(
                        cell,
                        style
                    )
                )

            else:

                table_row.append(cell)

        table_data.append(
            table_row
        )

    table = Table(
        table_data,
        colWidths=widths,
        repeatRows=1,
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
            6,
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            6,
        ),
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

    for row in range(
        1,
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


def add_page_number(
    canvas,
    document
):

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


def build_device_summary(report):

    summary = {}

    for incident in report.get(
        "incidents",
        []
    ):

        object_types = incident.get(
            "object_types",
            {}
        )

        duration = int(
            incident.get(
                "duration",
                0
            )
        )

        for object_name in incident.get(
            "objects",
            []
        ):

            if object_types.get(
                object_name
            ) != "device":

                continue

            if object_name not in summary:

                summary[object_name] = {
                    "device": object_name,
                    "events": 0,
                    "downtime": 0,
                }

            summary[object_name]["events"] += 1

            summary[object_name]["downtime"] += (
                duration
            )

    reliability = {}

    for device in report.get(
        "device_reliability",
        []
    ):

        device_name = device.get(
            "device"
        )

        if device_name:

            reliability[device_name] = device

    result = []

    for device_name, data in summary.items():

        device_reliability = reliability.get(
            device_name,
            {}
        )

        result.append(
            {
                "device": device_name,
                "events": data["events"],
                "downtime": data["downtime"],
                "score": device_reliability.get(
                    "score",
                    0
                ),
                "health": device_reliability.get(
                    "health",
                    "-"
                ),
            }
        )

    result.sort(
        key=lambda item: (
            -item["events"],
            -item["downtime"],
            item["device"].lower()
        )
    )

    return result


def build_service_summary(report):

    summary = {}

    #
    # Start with every configured network gateway so that
    # important infrastructure is shown even when it has
    # never experienced an outage.
    #

    for network in config.get_networks():

        gateway_name = network.get(
            "gateway_name"
        )

        if not gateway_name:

            continue

        if gateway_name == "OPNSense":

            display_name = "OPNsense Firewall"

        elif gateway_name == "DIGIBox":

            display_name = "DIGIBox WAN Gateway"

        else:

            display_name = gateway_name

        summary[gateway_name] = {
            "service": display_name,
            "events": 0,
            "downtime": 0,
        }

    #
    # Add recorded service outage information.
    #

    for outage in report.get(
        "service_outages",
        []
    ):

        duration = int(
            outage.get(
                "duration",
                0
            )
        )

        objects = outage.get(
            "objects",
            []
        )

        for object_name in objects:

            if object_name not in summary:

                summary[object_name] = {
                    "service": (
                        "OPNsense Firewall"
                        if object_name == "OPNSense"
                        else object_name
                    ),
                    "events": 0,
                    "downtime": 0,
                }

            summary[object_name]["events"] += 1

            summary[object_name]["downtime"] += (
                duration
            )

    result = list(
        summary.values()
    )

    result.sort(
        key=lambda item: (
            -item["events"],
            -item["downtime"],
            item["service"].lower()
        )
    )

    return result

def generate_device_report(
    report,
    output_path=None
):

    customer = config.load_customer()

    customer_name = customer.get(
        "customer",
        "Customer"
    )

    address = customer.get(
        "address",
        ""
    )

    if output_path is None:

        customer_filename = safe_filename(
            customer_name
        )

        output_path = os.path.join(
            REPORT_DIR,
            (
                f"{customer_filename}"
                "_Device_Incident_Summary.pdf"
            )
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
        title="Device Incident Summary",
        author="Scout Network Monitor",
    )

    story = []

    story.append(
        Spacer(1, 8 * mm)
    )

    story.append(
        Paragraph(
            "DEVICE INCIDENT SUMMARY",
            styles["DeviceReportTitle"]
        )
    )

    story.append(
        Paragraph(
            "Scout Network Monitor",
            styles["DeviceReportSubtitle"]
        )
    )

    story.append(
        Spacer(1, 7 * mm)
    )

    customer_data = [
        [
            Paragraph(
                "<b>Customer</b>",
                styles["DeviceSmall"]
            ),
            Paragraph(
                str(customer_name),
                styles["DeviceSmall"]
            ),
        ],
        [
            Paragraph(
                "<b>Site / Address</b>",
                styles["DeviceSmall"]
            ),
            Paragraph(
                str(address) if address else "-",
                styles["DeviceSmall"]
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
    # Network Service Availability
    #

    story.append(
        Paragraph(
            "Network Service Availability",
            styles["DeviceSectionHeading"]
        )
    )

    service_summary = build_service_summary(
        report
    )

    if service_summary:

        story.append(
            Paragraph(
                (
                    "The following network services were "
                    "included in recorded service outage "
                    "events during the analysis period."
                ),
                styles["DeviceBody"]
            )
        )

        service_data = [
            [
                "Service",
                "Events",
                "Total Downtime",
            ]
        ]

        for service in service_summary:

            service_data.append(
                [
                    str(
                        service.get(
                            "service",
                            "-"
                        )
                    ),
                    str(
                        service.get(
                            "events",
                            0
                        )
                    ),
                    format_duration(
                        service.get(
                            "downtime",
                            0
                        )
                    ),
                ]
            )

        story.append(
            make_table(
                service_data,
                widths=[
                    95 * mm,
                    30 * mm,
                    47 * mm,
                ]
            )
        )

    else:

        story.append(
            Paragraph(
                (
                    "No network service outage events were "
                    "recorded during the analysis period."
                ),
                styles["DeviceBody"]
            )
        )

    #
    # Device Incidents
    #

    story.append(
        Paragraph(
            "Device Incidents",
            styles["DeviceSectionHeading"]
        )
    )

    story.append(
        Paragraph(
            (
                "The following monitored devices were "
                "included in one or more incident periods "
                "during the analysis period."
            ),
            styles["DeviceBody"]
        )
    )

    device_summary = build_device_summary(
        report
    )

    if device_summary:

        device_data = [
            [
                "Device",
                "Events",
                "Total Downtime",
                "Reliability",
                "Health",
            ]
        ]

        for device in device_summary:

            device_data.append(
                [
                    str(
                        device.get(
                            "device",
                            "-"
                        )
                    ),
                    str(
                        device.get(
                            "events",
                            0
                        )
                    ),
                    format_duration(
                        device.get(
                            "downtime",
                            0
                        )
                    ),
                    f"{device.get('score', 0)}%",
                    str(
                        device.get(
                            "health",
                            "-"
                        )
                    ),
                ]
            )

        story.append(
            make_table(
                device_data,
                widths=[
                    70 * mm,
                    22 * mm,
                    32 * mm,
                    25 * mm,
                    25 * mm,
                ]
            )
        )

    else:

        story.append(
            Paragraph(
                (
                    "No monitored devices were included in "
                    "a recorded incident period during the "
                    "analysis period."
                ),
                styles["DeviceBody"]
            )
        )

    story.append(
        Spacer(1, 6 * mm)
    )

    story.append(
        Paragraph(
            (
                "The incident count represents the number "
                "of recorded incident periods in which the "
                "device was identified as affected. Total "
                "downtime is the combined duration of those "
                "incident periods."
            ),
            styles["DeviceSmall"]
        )
    )

    story.append(
        Paragraph(
            (
                "The service information describes observed "
                "availability events for the monitored "
                "services. It does not establish the physical "
                "or technical root cause of an incident."
            ),
            styles["DeviceSmall"]
        )
    )

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return output_path