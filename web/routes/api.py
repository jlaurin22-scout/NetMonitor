#!/usr/bin/env python3

from flask import Blueprint, jsonify

from web.routes.dashboard import (
    build_network_status,
    build_status_rows,
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

    up_devices = sum(
        1
        for row in device_rows
        if row["state"] == "UP"
    )

    down_devices = (
        len(device_rows)
        -
        up_devices
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

    for row in device_rows:

        devices.append(
            {
                "name": row["name"],
                "state": row["state"],
                "job_type": row["job_type"],
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
                "total": len(device_rows),
                "up": up_devices,
                "down": down_devices,
                "rows": devices,
            },
            "networks": network_data,
        }
    )