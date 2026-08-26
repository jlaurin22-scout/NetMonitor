#!/usr/bin/env python3

from flask import Blueprint, jsonify

from engine import config
from engine import database

from web.routes.dashboard import (
    build_network_status,
    build_status_rows,
    get_active_incidents,
    get_device_counts,
    get_service_state,
    overall_health,
)


api = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


@api.route("/status")
def status():

    rows = build_status_rows()

    service_state, service_up = (
        get_service_state()
    )

    networks = build_network_status(
        rows
    )

    incidents = database.get_incidents()

    active_incidents = get_active_incidents(
        incidents
    )

    device_rows = [
        row
        for row in rows
        if row["job_type"] == "device"
    ]

    (
        device_total,
        up_devices,
        down_devices,
        standby_count
    ) = get_device_counts(
        device_rows
    )

    health = overall_health(
        service_up,
        rows
    )

    network_data = []

    for network in networks:

        network_data.append(
            {
                "name": network["name"],
                "healthy": all(
                    item is None
                    or item["state"] == "UP"
                    for item in [
                        network["gateway"],
                        network["internet"],
                        network["dns"],
                    ]
                ),
                "gateway": (
                    network["gateway"]["state"]
                    if network["gateway"]
                    else None
                ),
                "internet": (
                    network["internet"]["state"]
                    if network["internet"]
                    else None
                ),
                "dns": (
                    network["dns"]["state"]
                    if network["dns"]
                    else None
                ),
            }
        )

    devices = []

    configured_devices = config.get_devices()

    device_modes = {
        device.get("name"): config.get_device_monitoring_mode(
            device
        )
        for device in configured_devices
    }

    for row in device_rows:

        devices.append(
            {
                "name": row["name"],
                "state": row["state"],
                "job_type": row["job_type"],
                "monitoring_mode": device_modes.get(
                    row["name"],
                    "normal"
                ),
            }
        )

    incident_data = []

    for incident in active_incidents:

        primary = incident.get(
            "primary"
        )

        incident_data.append(
            {
                "start": incident.get(
                    "start"
                ),
                "duration": incident.get(
                    "duration"
                ),
                "primary": (
                    {
                        "object": primary.get(
                            "object"
                        ),
                        "job_type": primary.get(
                            "job_type"
                        ),
                        "network": primary.get(
                            "network"
                        ),
                        "confidence": primary.get(
                            "confidence"
                        ),
                    }
                    if primary
                    else None
                ),
                "dependents": [
                    {
                        "object": item.get(
                            "object"
                        ),
                        "job_type": item.get(
                            "job_type"
                        ),
                        "network": item.get(
                            "network"
                        ),
                        "delay": item.get(
                            "delay"
                        ),
                    }
                    for item in incident.get(
                        "dependents",
                        []
                    )
                ],
                "secondary": [
                    {
                        "object": item.get(
                            "object"
                        ),
                        "job_type": item.get(
                            "job_type"
                        ),
                        "network": item.get(
                            "network"
                        ),
                        "delay": item.get(
                            "delay"
                        ),
                    }
                    for item in incident.get(
                        "secondary",
                        []
                    )
                ],
                "flapping": [
                    {
                        "object": item.get(
                            "object"
                        ),
                        "episodes": item.get(
                            "episodes"
                        ),
                    }
                    for item in incident.get(
                        "flapping",
                        []
                    )
                ],
                "diagnosis": incident.get(
                    "diagnosis",
                    "No diagnosis available."
                ),
                "objects": sorted(
                    incident.get(
                        "objects",
                        []
                    )
                ),
            }
        )

    return jsonify(
        {
            "health": health,
            "service": {
                "state": service_state,
                "up": service_up,
            },
            "devices": {
                "total": device_total,
                "up": up_devices,
                "down": down_devices,
                "standby": standby_count,
                "rows": devices,
            },
            "networks": network_data,
            "incidents": incident_data,
        }
    )
