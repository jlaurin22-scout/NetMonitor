#!/usr/bin/env python3

import subprocess

from flask import Blueprint, render_template

from engine import config
from engine import database
from engine.analysis.incidents import network_from_name


dashboard = Blueprint(
    "dashboard",
    __name__
)


def get_service_state():

    result = subprocess.run(
        [
            "systemctl",
            "is-active",
            "netmonitor"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:

        return "RUNNING", True

    return "DOWN", False


def display_name(name):

    if ":" in name:

        prefix, device_name = name.split(
            ":",
            1
        )

        try:

            int(prefix)

            return device_name

        except ValueError:

            pass

    return name


def build_status_rows():

    rows = database.get_current_status()

    result = []

    for row in rows:

        name = row["job_name"]

        result.append(
            {
                "name": display_name(name),
                "job_name": name,
                "job_type": row["job_type"],
                "state": row["state"],
                "last_change": row["last_change"],
            }
        )

    return result


def build_network_status(rows):

    networks = {}

    configured_networks = config.get_networks()
    configured_devices = config.get_devices()
    settings = config.load_settings()

    for network in configured_networks:

        name = network.get(
            "name",
            f"Network {network.get('id', '')}"
        )

        networks[name] = {
            "name": name,
            "gateway": None,
            "internet": None,
            "dns": None,
            "devices": [],
        }

    for row in rows:

        job_type = row["job_type"]
        job_name = row["job_name"]

        network_name = network_from_name(
            job_name,
            configured_networks,
            configured_devices
        )

        if network_name is None:

            if job_name.startswith("LAN "):

                network_name = "LAN"

            elif job_name.startswith("WAN "):

                network_name = "WAN"

        if network_name is None:

            continue

        if network_name not in networks:

            networks[network_name] = {
                "name": network_name,
                "gateway": None,
                "internet": None,
                "dns": None,
                "devices": [],
            }

        network_config = next(
            (
                network
                for network in configured_networks
                if network.get("name") == network_name
            ),
            None
        )

        row = dict(row)

        if job_type == "gateway":

            if network_config is not None:

                row["target_name"] = network_config.get(
                    "gateway_name",
                    "Gateway"
                )

                row["target_ip"] = network_config.get(
                    "gateway",
                    ""
                )

            networks[
                network_name
            ]["gateway"] = row

        elif job_type == "internet":

            internet_settings = settings.get(
                "internet",
                {}
            )

            targets = internet_settings.get(
                "targets",
                []
            )

            row["targets"] = targets

            networks[
                network_name
            ]["internet"] = row

        elif job_type == "dns":

            if network_config is not None:

                dns_servers = network_config.get(
                    "dns",
                    []
                )

                if dns_servers:

                    row["target_ip"] = dns_servers[0]

            networks[
                network_name
            ]["dns"] = row

        elif job_type == "device":

            networks[
                network_name
            ]["devices"].append(row)

    return list(networks.values())


def network_is_healthy(network):

    checks = [
        network["gateway"],
        network["internet"],
        network["dns"],
    ]

    checks = [
        item
        for item in checks
        if item is not None
    ]

    if not checks:

        return True

    return all(
        item["state"] == "UP"
        for item in checks
    )


def get_standby_devices():

    devices = config.get_devices()

    standby = set()

    for device in devices:

        if (
            config.get_device_monitoring_mode(device)
            ==
            "standby"
        ):

            standby.add(
                device.get("name")
            )

    return standby


def is_standby_device(row, standby_devices):

    if row["job_type"] != "device":

        return False

    return (
        display_name(
            row["job_name"]
        )
        in standby_devices
    )


def get_active_incidents(
    incidents
):

    active = []

    for incident in incidents:

        episodes = incident.get(
            "episodes",
            []
        )

        if any(
            episode.get("end") is None
            for episode in episodes
        ):

            active.append(
                incident
            )

    return active


def overall_health(
    service_up,
    rows
):

    if not service_up:

        return {
            "label": "MONITORING DOWN",
            "class": "state-down",
        }

    standby_devices = get_standby_devices()

    for row in rows:

        if (
            row["state"] != "UP"
            and
            not is_standby_device(
                row,
                standby_devices
            )
        ):

            return {
                "label": "ATTENTION",
                "class": "state-warning",
            }

    return {
        "label": "HEALTHY",
        "class": "state-up",
    }


def get_device_counts(device_rows):

    standby_devices = get_standby_devices()

    monitored_devices = [
        row
        for row in device_rows
        if not is_standby_device(
            row,
            standby_devices
        )
    ]

    up_devices = sum(
        1
        for row in monitored_devices
        if row["state"] == "UP"
    )

    down_devices = sum(
        1
        for row in monitored_devices
        if row["state"] != "UP"
    )

    standby_count = sum(
        1
        for row in device_rows
        if is_standby_device(
            row,
            standby_devices
        )
    )

    return (
        len(device_rows),
        up_devices,
        down_devices,
        standby_count
    )


@dashboard.route("/")
def index():

    customer_data = config.load_customer()

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

    return render_template(
        "dashboard.html",
        customer=customer_data.get(
            "customer",
            "Unknown"
        ),
        address=customer_data.get(
            "address",
            ""
        ),
        service_state=service_state,
        service_up=service_up,
        health=health,
        networks=networks,
        device_total=device_total,
        up_devices=up_devices,
        down_devices=down_devices,
        standby_count=standby_count,
        devices=device_rows[:8],
        active_incidents=active_incidents,
    )