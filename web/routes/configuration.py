#!/usr/bin/env python3

import json
import subprocess

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)

from engine import config
from engine import database

from web.auth import admin_required


configuration = Blueprint(
    "configuration",
    __name__,
    url_prefix="/configuration"
)


MONITORING_MODES = {
    "normal": "NORMAL",
    "standby": "STANDBY",
    "conditional": "CONDITIONAL",
}


def _restart_monitoring():

    result = subprocess.run(
        [
            "/usr/bin/sudo",
            "-n",
            "/usr/local/sbin/netmonitor-web-restart"
        ],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def _restart_netmonitor():

    result = subprocess.run(
        [
            "/usr/bin/sudo",
            "-n",
            "/usr/local/sbin/netmonitor-web-restart"
        ],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def _run_speed_test():

    result = subprocess.run(
        [
            "/usr/bin/speedtest-cli",
            "--json"
        ],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:

        error = (
            result.stderr.strip()
            or
            result.stdout.strip()
            or
            "Speed test failed."
        )

        raise Exception(error)

    try:

        data = json.loads(
            result.stdout
        )

    except json.JSONDecodeError:

        raise Exception(
            "Speed test returned invalid data."
        )

    server = data.get(
        "server",
        {}
    )

    return {
        "download": round(
            data.get(
                "download",
                0
            ) / 1000000,
            2
        ),
        "upload": round(
            data.get(
                "upload",
                0
            ) / 1000000,
            2
        ),
        "ping": round(
            data.get(
                "ping",
                0
            ),
            2
        ),
        "server": server.get(
            "name",
            "Unknown"
        ),
        "country": server.get(
            "country",
            ""
        ),
        "sponsor": server.get(
            "sponsor",
            ""
        ),
        "timestamp": data.get(
            "timestamp",
            ""
        ),
    }


def _device_rows():

    devices = config.get_devices()
    networks = config.get_networks()

    network_map = {
        network["id"]: network
        for network in networks
    }

    status_map = {
        row["job_name"]: row["state"]
        for row in database.get_current_status()
        if row["job_type"] == "device"
    }

    rows = []

    for device in devices:

        network_id = device.get(
            "network_id",
            1
        )

        mode = config.get_device_monitoring_mode(
            device
        )

        job_name = (
            f"{network_id}:"
            f"{device['name']}"
        )

        state = status_map.get(
            job_name,
            "UNKNOWN"
        )

        rows.append(
            {
                "id": device["id"],
                "name": device["name"],
                "ip": device["ip"],
                "network_id": network_id,
                "network_name": network_map.get(
                    network_id,
                    {}
                ).get(
                    "name",
                    "Unknown"
                ),
                "ping": device.get(
                    "checks",
                    {}
                ).get(
                    "ping",
                    False
                ),
                "snmp": device.get(
                    "checks",
                    {}
                ).get(
                    "snmp",
                    False
                ),
                "monitoring_mode": mode,
                "monitoring_label": MONITORING_MODES[mode],
                "state": (
                    "STANDBY"
                    if mode == "standby"
                    else state
                ),
            }
        )

    return rows


def _find_device(device_id):

    for device in config.get_devices():

        if device["id"] == device_id:

            return device

    return None


def _find_network(network_id):

    for network in config.get_networks():

        if network["id"] == network_id:

            return network

    return None


def _render_configuration(page):

    customer = config.load_customer()

    return render_template(
        "configuration.html",
        page=page,
        customer=customer.get(
            "customer",
            "Unknown"
        ),
        address=customer.get(
            "address",
            ""
        ),
        networks=config.get_networks(),
        devices=_device_rows(),
        settings=config.load_settings(),
        internet_targets=config.get_internet_targets(),
    )


@configuration.route("/")
def index():

    return _render_configuration(
        "configuration"
    )


@configuration.route("/customer")
def customer():

    return _render_configuration(
        "customer"
    )


@configuration.route("/customer/save", methods=["POST"])
@admin_required
def save_customer():

    customer = request.form.get(
        "customer",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()

    if not customer:

        return redirect(
            url_for(
                "configuration.customer",
                error="Customer name cannot be empty."
            )
        )

    config.update_customer(
        customer,
        address
    )

    return redirect(
        url_for(
            "configuration.customer",
            message="Customer information updated successfully."
        )
    )


@configuration.route("/networks")
def networks():

    return _render_configuration(
        "networks"
    )


@configuration.route("/networks/add", methods=["POST"])
@admin_required
def add_network():

    try:

        name = request.form.get(
            "name",
            ""
        ).strip()

        interface = request.form.get(
            "interface",
            ""
        ).strip()

        ip = request.form.get(
            "ip",
            ""
        ).strip()

        prefix = int(
            request.form.get(
                "prefix",
                "0"
            )
        )

        gateway = request.form.get(
            "gateway",
            ""
        ).strip()

        gateway_name = request.form.get(
            "gateway_name",
            ""
        ).strip()

        dns1 = request.form.get(
            "dns1",
            ""
        ).strip()

        dns2 = request.form.get(
            "dns2",
            ""
        ).strip()

        config.add_network(
            name,
            interface,
            ip,
            prefix,
            gateway,
            gateway_name,
            [
                dns1,
                dns2
            ]
        )

        restarted = _restart_netmonitor()

        message = (
            "Network added successfully."
            if restarted
            else
            "Network saved. Restart NetMonitor to apply the change."
        )

        return redirect(
            url_for(
                "configuration.networks",
                message=message
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.networks",
                error=str(e)
            )
        )


@configuration.route(
    "/networks/<int:network_id>/edit",
    methods=["POST"]
)
@admin_required
def edit_network(network_id):

    selected = _find_network(
        network_id
    )

    if selected is None:

        return redirect(
            url_for(
                "configuration.networks",
                error="Network not found."
            )
        )

    try:

        name = request.form.get(
            "name",
            ""
        ).strip()

        interface = request.form.get(
            "interface",
            ""
        ).strip()

        ip = request.form.get(
            "ip",
            ""
        ).strip()

        prefix = int(
            request.form.get(
                "prefix",
                "0"
            )
        )

        gateway = request.form.get(
            "gateway",
            ""
        ).strip()

        gateway_name = request.form.get(
            "gateway_name",
            ""
        ).strip()

        dns1 = request.form.get(
            "dns1",
            ""
        ).strip()

        dns2 = request.form.get(
            "dns2",
            ""
        ).strip()

        config.update_network(
            network_id,
            name,
            interface,
            ip,
            prefix,
            gateway,
            gateway_name,
            [
                dns1,
                dns2
            ]
        )

        restarted = _restart_netmonitor()

        message = (
            "Network updated successfully."
            if restarted
            else
            "Network saved. Restart NetMonitor to apply the change."
        )

        return redirect(
            url_for(
                "configuration.networks",
                message=message
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.networks",
                error=str(e)
            )
        )


@configuration.route(
    "/networks/<int:network_id>/remove",
    methods=["POST"]
)
@admin_required
def remove_network(network_id):

    selected = _find_network(
        network_id
    )

    if selected is None:

        return redirect(
            url_for(
                "configuration.networks",
                error="Network not found."
            )
        )

    try:

        config.remove_network(
            network_id
        )

        restarted = _restart_netmonitor()

        message = (
            "Network removed successfully."
            if restarted
            else
            "Network removed. Restart NetMonitor to apply the change."
        )

        return redirect(
            url_for(
                "configuration.networks",
                message=message
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.networks",
                error=str(e)
            )
        )


@configuration.route("/monitoring")
def monitoring():

    return _render_configuration(
        "monitoring"
    )


@configuration.route(
    "/monitoring/save",
    methods=["POST"]
)
@admin_required
def save_monitoring():

    try:

        gateway_interval = int(
            request.form.get(
                "gateway_interval",
                "0"
            )
        )

        internet_interval = int(
            request.form.get(
                "internet_interval",
                "0"
            )
        )

        dns_interval = int(
            request.form.get(
                "dns_interval",
                "0"
            )
        )

        device_interval = int(
            request.form.get(
                "device_interval",
                "0"
            )
        )

        intervals = [
            gateway_interval,
            internet_interval,
            dns_interval,
            device_interval
        ]

        if any(
            interval < 1
            for interval in intervals
        ):

            raise ValueError(
                "Monitoring intervals must be at least 1 second."
            )

        config.update_monitoring_intervals(
            gateway_interval,
            internet_interval,
            dns_interval,
            device_interval
        )

        restarted = _restart_netmonitor()

        message = (
            "Monitoring settings updated successfully."
            if restarted
            else
            "Monitoring settings saved. Restart NetMonitor to apply the change."
        )

        return redirect(
            url_for(
                "configuration.monitoring",
                message=message
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.monitoring",
                error=str(e)
            )
        )


@configuration.route("/internet")
def internet():

    return _render_configuration(
        "internet"
    )


@configuration.route(
    "/internet/targets/add",
    methods=["POST"]
)
@admin_required
def add_internet_target():

    try:

        ip = request.form.get(
            "ip",
            ""
        ).strip()

        config.add_internet_target(
            ip
        )

        restarted = _restart_netmonitor()

        message = (
            "Internet target added successfully."
            if restarted
            else
            "Internet target saved. Restart NetMonitor to apply the change."
        )

        return redirect(
            url_for(
                "configuration.internet",
                message=message
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.internet",
                error=str(e)
            )
        )


@configuration.route(
    "/internet/targets/<path:ip>/remove",
    methods=["POST"]
)
@admin_required
def remove_internet_target(ip):

    try:

        config.remove_internet_target(
            ip
        )

        restarted = _restart_netmonitor()

        message = (
            "Internet target removed successfully."
            if restarted
            else
            "Internet target removed. Restart NetMonitor to apply the change."
        )

        return redirect(
            url_for(
                "configuration.internet",
                message=message
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.internet",
                error=str(e)
            )
        )


@configuration.route(
    "/internet/speedtest",
    methods=["POST"]
)
@admin_required
def internet_speedtest():

    try:

        result = _run_speed_test()

        return render_template(
            "configuration.html",
            page="internet",
            customer=config.load_customer().get(
                "customer",
                "Unknown"
            ),
            address=config.load_customer().get(
                "address",
                ""
            ),
            networks=config.get_networks(),
            devices=_device_rows(),
            settings=config.load_settings(),
            internet_targets=config.get_internet_targets(),
            speedtest=result,
        )

    except subprocess.TimeoutExpired:

        return redirect(
            url_for(
                "configuration.internet",
                error="Internet speed test timed out."
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.internet",
                error=str(e)
            )
        )


@configuration.route("/devices")
def devices():

    return _render_configuration(
        "devices"
    )


@configuration.route("/devices/add", methods=["POST"])
@admin_required
def add_device():

    try:

        config.add_device(
            name=request.form.get(
                "name",
                ""
            ).strip(),
            ip=request.form.get(
                "ip",
                ""
            ).strip(),
            ping=request.form.get(
                "ping"
            ) == "on",
            snmp=request.form.get(
                "snmp"
            ) == "on",
            network_id=int(
                request.form.get(
                    "network_id",
                    "0"
                )
            ),
            monitoring_mode=request.form.get(
                "monitoring_mode",
                "normal"
            )
        )

        restarted = _restart_monitoring()

        message = (
            "Device added successfully."
            if restarted
            else
            "Device saved. Restart NetMonitor to apply the change."
        )

        return redirect(
            url_for(
                "configuration.devices",
                message=message
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.devices",
                error=str(e)
            )
        )


@configuration.route(
    "/devices/<int:device_id>/edit",
    methods=["POST"]
)
@admin_required
def edit_device(device_id):

    selected = _find_device(device_id)

    if selected is None:

        return redirect(
            url_for(
                "configuration.devices",
                error="Device not found."
            )
        )

    old_network_id = selected.get(
        "network_id",
        1
    )

    old_name = selected["name"]

    try:

        new_name = request.form.get(
            "name",
            ""
        ).strip()

        new_ip = request.form.get(
            "ip",
            ""
        ).strip()

        new_network_id = int(
            request.form.get(
                "network_id",
                "0"
            )
        )

        new_mode = request.form.get(
            "monitoring_mode",
            "normal"
        )

        config.update_device(
            device_id,
            new_name,
            new_ip,
            request.form.get("ping") == "on",
            request.form.get("snmp") == "on",
            new_network_id,
            new_mode
        )

        if (
            old_name != new_name
            or
            old_network_id != new_network_id
        ):

            database.remove_status(
                f"{old_network_id}:{old_name}"
            )

        restarted = _restart_monitoring()

        message = (
            "Device updated successfully."
            if restarted
            else
            "Device saved. Restart NetMonitor to apply the change."
        )

        return redirect(
            url_for(
                "configuration.devices",
                message=message
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.devices",
                error=str(e)
            )
        )


@configuration.route(
    "/devices/<int:device_id>/remove",
    methods=["POST"]
)
@admin_required
def remove_device(device_id):

    selected = _find_device(device_id)

    if selected is None:

        return redirect(
            url_for(
                "configuration.devices",
                error="Device not found."
            )
        )

    try:

        removed = config.remove_device(
            device_id
        )

        network_id = removed.get(
            "network_id",
            1
        )

        database.remove_status(
            f"{network_id}:{removed['name']}"
        )

        restarted = _restart_monitoring()

        message = (
            "Device removed successfully."
            if restarted
            else
            "Device removed. Restart NetMonitor to apply the change."
        )

        return redirect(
            url_for(
                "configuration.devices",
                message=message
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "configuration.devices",
                error=str(e)
            )
        )