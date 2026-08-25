#!/usr/bin/env python3

from flask import Blueprint, jsonify

from engine import config

from web.routes.dashboard import (
    build_network_status,
    build_status_rows,
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
        }
    )