#!/usr/bin/env python3

import json
import os
import socket
import subprocess
import syslog
import threading
import time
from datetime import datetime

from engine import config
from engine.constants import BUILD, VERSION


NOTIFY_STATE = "/var/lib/netmonitor/notify_state.json"
NETWORK_CHECK_INTERVAL = 30
RESTART_REASON_FILE = "/var/lib/netmonitor/restart_reason.json"


def set_restart_reason(
    reason,
    details=""
):

    data = {
        "reason": reason,
        "details": details
    }

    try:

        with open(
            RESTART_REASON_FILE,
            "w"
        ) as f:

            json.dump(
                data,
                f
            )

    except OSError as e:

        syslog.syslog(
            f"NetMonitor: could not save restart reason: {e}"
        )


def get_restart_reason():

    try:

        with open(
            RESTART_REASON_FILE,
            "r"
        ) as f:

            return json.load(f)

    except (
        OSError,
        json.JSONDecodeError
    ):

        return None


def clear_restart_reason():

    try:

        os.remove(
            RESTART_REASON_FILE
        )

    except FileNotFoundError:

        pass

    except OSError as e:

        syslog.syslog(
            f"NetMonitor: could not clear restart reason: {e}"
        )



def _load_ntfy_settings():

    settings = config.load_settings()

    return settings.get(
        "ntfy",
        {}
    )



def _notification_enabled(setting):

    ntfy = _load_ntfy_settings()

    return (
        ntfy.get("enabled", False)
        and
        ntfy.get(setting, True)
    )



def _run_json(command):

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:

        return []

    try:

        return json.loads(
            result.stdout
        )

    except (json.JSONDecodeError, TypeError):

        return []



def get_interface_ipv4(interface):

    data = _run_json(
        [
            "ip",
            "-j",
            "-4",
            "addr",
            "show",
            "dev",
            interface
        ]
    )

    addresses = []

    for item in data:

        for address in item.get("addr_info", []):

            local = address.get(
                "local",
                ""
            )

            if local:

                addresses.append(local)

    return addresses



def get_tailscale_ip():

    addresses = get_interface_ipv4(
        "tailscale0"
    )

    if addresses:

        return addresses[0]

    result = subprocess.run(
        [
            "tailscale",
            "ip",
            "-4"
        ],
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode == 0:

        for line in result.stdout.splitlines():

            value = line.strip()

            if value:

                return value

    return ""



def get_watchdog_ip_for_network(network):

    interface = network.get(
        "interface",
        ""
    ).strip()

    if interface:

        addresses = get_interface_ipv4(
            interface
        )

        if addresses:

            return addresses[0]

    return network.get(
        "ip",
        "Unknown"
    )


def get_notification_ip():

    networks = config.get_networks()

    if networks:

        networks = sorted(
            networks,
            key=lambda network: network.get("id", 999999)
        )

        interface = networks[0].get(
            "interface",
            ""
        ).strip()

        if interface:

            addresses = get_interface_ipv4(
                interface
            )

            if addresses:

                return addresses[0]

        ip = networks[0].get(
            "ip",
            ""
        ).strip()

        if ip:

            return ip

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:

        s.connect(
            ("1.1.1.1", 80)
        )

        return s.getsockname()[0]

    finally:

        s.close()



def get_network_snapshot():

    networks = config.get_networks()

    snapshot = []

    for network in sorted(
        networks,
        key=lambda item: item.get("id", 999999)
    ):

        interface = network.get(
            "interface",
            ""
        ).strip()

        actual_ips = get_interface_ipv4(
            interface
        ) if interface else []

        snapshot.append({
            "id": network.get("id"),
            "name": network.get("name", "Network"),
            "interface": interface,
            "configured_ip": network.get("ip", ""),
            "actual_ips": actual_ips,
            "prefix": network.get("prefix", ""),
            "gateway": network.get("gateway", ""),
            "gateway_name": network.get("gateway_name", "Gateway"),
            "dns": [
                dns
                for dns in network.get("dns", [])
                if dns
            ]
        })

    return snapshot



def get_system_uptime():

    try:

        with open(
            "/proc/uptime",
            "r"
        ) as f:

            seconds = int(
                float(
                    f.read().split()[0]
                )
            )

        days, remainder = divmod(
            seconds,
            86400
        )

        hours, remainder = divmod(
            remainder,
            3600
        )

        minutes = remainder // 60

        parts = []

        if days:

            parts.append(
                f"{days}d"
            )

        if hours or days:

            parts.append(
                f"{hours}h"
            )

        parts.append(
            f"{minutes}m"
        )

        return " ".join(parts)

    except Exception:

        return "Unknown"



def get_boot_time():

    try:

        with open(
            "/proc/stat",
            "r"
        ) as f:

            for line in f:

                if line.startswith("btime "):

                    timestamp = int(
                        line.split()[1]
                    )

                    return datetime.fromtimestamp(
                        timestamp
                    ).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

    except Exception:

        pass

    return "Unknown"



def get_watchdog_identity():

    settings = config.load_settings()
    ntfy = settings.get(
        "ntfy",
        {}
    )
    customer = config.load_customer()
    devices = config.get_devices()

    name = ntfy.get(
        "name",
        ""
    ).strip()

    if not name:

        name = "Watchdog"

    location = ntfy.get(
        "location",
        ""
    ).strip()

    if not location:

        location = "Not configured"

    return {
        "name": name,
        "location": location,
        "hostname": socket.gethostname(),
        "version": VERSION,
        "build": BUILD,
        "customer": customer.get(
            "customer",
            ""
        ),
        "uptime": get_system_uptime(),
        "boot_time": get_boot_time(),
        "tailscale_ip": get_tailscale_ip(),
        "networks": get_network_snapshot(),
        "device_count": len(devices)
    }



def _resolve_ntfy_ipv4(
    server,
    dns_server,
    interface
):

    try:

        import dns.resolver

        hostname = server.split(
            "://",
            1
        )[-1].split(
            "/",
            1
        )[0]

        resolver = dns.resolver.Resolver(
            configure=False
        )

        resolver.nameservers = [
            dns_server
        ]

        resolver.timeout = 2
        resolver.lifetime = 3

        answers = resolver.resolve(
            hostname,
            "A"
        )

        for answer in answers:

            address = answer.address

            if address:

                return address

    except Exception as e:

        syslog.syslog(
            f"NetMonitor: NTFY DNS resolution failed "
            f"via {interface} ({dns_server}): {e}"
        )

    return ""


def _send_ntfy_request(
    url,
    title,
    message,
    token,
    tags,
    priority,
    interface=None,
    resolved_ip=None
):

    command = [
        "curl",
        "-s",
        "-o",
        "/dev/null",
        "-w",
        "%{http_code}",
        "--max-time",
        "5",
        "-X",
        "POST",
        "-H",
        f"Title: {title}",
        "-d",
        message
    ]

    if resolved_ip:

        from urllib.parse import urlparse

        parsed = urlparse(url)

        command.extend(
            [
                "--resolve",
                f"{parsed.hostname}:443:{resolved_ip}"
            ]
        )

    if interface:

        command.extend(
            [
                "--interface",
                interface
            ]
        )

    if tags:

        command.extend(
            [
                "-H",
                f"Tags: {tags}"
            ]
        )

    if priority:

        command.extend(
            [
                "-H",
                f"Priority: {priority}"
            ]
        )

    if token:

        command.extend(
            [
                "-H",
                f"Authorization: Bearer {token}"
            ]
        )

    command.append(
        url
    )

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False
    )

    return (
        result.returncode == 0
        and
        result.stdout.startswith("2")
    )


def send_ntfy(
    server,
    topic,
    token,
    title,
    message,
    tags=None,
    priority=None
):

    url = (
        f"{server.rstrip('/')}/"
        f"{topic}"
    )

    success = _send_ntfy_request(
        url,
        title,
        message,
        token,
        tags,
        priority
    )

    if success:

        syslog.syslog(
            "NetMonitor: NTFY notification "
            "sent via default route"
        )

        return True

    syslog.syslog(
        "NetMonitor: NTFY notification "
        "failed via default route"
    )

    for network in config.get_networks():

        interface = network.get(
            "interface",
            ""
        ).strip()

        if not interface:

            continue

        dns_servers = [
            value
            for value in network.get(
                "dns",
                []
            )
            if value
        ]

        if not dns_servers:

            continue

        for dns_server in dns_servers:

            resolved_ip = _resolve_ntfy_ipv4(
                server,
                dns_server,
                interface
            )

            if not resolved_ip:

                continue

            success = _send_ntfy_request(
                url,
                title,
                message,
                token,
                tags,
                priority,
                interface,
                resolved_ip
            )

            if success:

                syslog.syslog(
                    f"NetMonitor: NTFY notification "
                    f"sent via {interface} "
                    f"using DNS {dns_server}"
                )

                return True

            syslog.syslog(
                f"NetMonitor: NTFY notification "
                f"failed via {interface} "
                f"using DNS {dns_server}"
            )

    return False


def _ntfy_connection():

    ntfy = _load_ntfy_settings()

    server = ntfy.get(
        "server",
        "https://ntfy.sh"
    ).strip()

    topic = ntfy.get(
        "topic",
        ""
    ).strip()

    token = ntfy.get(
        "token",
        ""
    ).strip()

    if not ntfy.get("enabled", False):

        return None

    if not server or not topic:

        return None

    return server, topic, token, ntfy



def _format_network_lines(networks):

    lines = []

    for network in networks:

        actual = network.get(
            "actual_ips",
            []
        )

        actual_text = (
            ", ".join(actual)
            if actual
            else "NONE"
        )

        dns = network.get(
            "dns",
            []
        )

        dns_text = (
            ", ".join(dns)
            if dns
            else "Not configured"
        )

        lines.extend([
            f"Network {network.get('id')}: {network.get('name')}",
            f"  Interface: {network.get('interface') or 'Not configured'}",
            f"  Configured IP: {network.get('configured_ip') or 'Not configured'}",
            f"  Actual IP: {actual_text}",
            f"  Gateway: {network.get('gateway') or 'Not configured'}",
            f"  DNS: {dns_text}"
        ])

    if not lines:

        lines.append(
            "No monitored networks configured."
        )

    return lines



def format_startup_message(identity):

    lines = [
        "WATCHDOG STARTED",
        "",
        f"Name: {identity['name']}",
        f"Location: {identity['location']}",
        f"Hostname: {identity['hostname']}",
        f"Version: {identity['version']}-{identity['build']}",
        f"Customer: {identity['customer'] or 'Not configured'}",
        f"Uptime: {identity['uptime']}",
        f"System boot: {identity['boot_time']}",
        f"Tailscale IP: {identity['tailscale_ip'] or 'Not available'}",
        f"Devices monitored: {identity['device_count']}",
        "",
        "NETWORKS"
    ]

    lines.extend(
        _format_network_lines(
            identity["networks"]
        )
    )

    lines.extend([
        "",
        f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ])

    return "\n".join(lines)



def _load_notify_state():

    try:

        with open(
            NOTIFY_STATE,
            "r"
        ) as f:

            return json.load(f)

    except (FileNotFoundError, json.JSONDecodeError, OSError):

        return {}



def _save_notify_state(snapshot):

    directory = os.path.dirname(
        NOTIFY_STATE
    )

    os.makedirs(
        directory,
        exist_ok=True
    )

    temporary = (
        f"{NOTIFY_STATE}.tmp"
    )

    with open(
        temporary,
        "w"
    ) as f:

        json.dump(
            snapshot,
            f,
            indent=4
        )

    os.replace(
        temporary,
        NOTIFY_STATE
    )



def _network_changes(previous, current):

    previous_map = {
        str(item.get("id")): item
        for item in previous
    }

    changes = []

    for network in current:

        key = str(
            network.get("id")
        )

        old = previous_map.get(
            key
        )

        if old is None:

            continue

        old_ips = old.get(
            "actual_ips",
            []
        )

        new_ips = network.get(
            "actual_ips",
            []
        )

        if old_ips != new_ips:

            changes.append({
                "network": network,
                "old_ips": old_ips,
                "new_ips": new_ips
            })

    return changes



def format_network_change_message(
    identity,
    changes
):

    lines = [
        "WATCHDOG NETWORK CHANGE",
        "",
        f"Name: {identity['name']}",
        f"Location: {identity['location']}",
        f"Hostname: {identity['hostname']}",
        f"Version: {identity['version']}-{identity['build']}",
        f"Tailscale IP: {identity['tailscale_ip'] or 'Not available'}",
        ""
    ]

    for change in changes:

        network = change["network"]
        old_ips = change["old_ips"]
        new_ips = change["new_ips"]

        lines.extend([
            f"Network: {network.get('name')}",
            f"Interface: {network.get('interface') or 'Unknown'}",
            f"Previous IP: {', '.join(old_ips) if old_ips else 'NONE'}",
            f"Current IP: {', '.join(new_ips) if new_ips else 'NONE'}",
            f"Configured IP: {network.get('configured_ip') or 'Not configured'}",
            f"Gateway: {network.get('gateway') or 'Not configured'}",
            ""
        ])

    lines.append(
        f"Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    return "\n".join(lines)



def send_network_change(changes):

    if not _notification_enabled(
        "notify_network_changes"
    ):

        return False

    connection = _ntfy_connection()

    if connection is None:

        return False

    server, topic, token, ntfy = connection
    identity = get_watchdog_identity()

    title = (
        f"⚠️ {identity['name']} — "
        f"NETWORK CHANGE"
    )

    return send_ntfy(
        server,
        topic,
        token,
        title,
        format_network_change_message(
            identity,
            changes
        ),
        tags="warning,network",
        priority="high"
    )



def _network_snapshot_loop():

    while True:

        try:

            current = get_network_snapshot()
            previous_state = _load_notify_state()
            previous = previous_state.get(
                "networks",
                []
            )

            changes = _network_changes(
                previous,
                current
            )

            if changes:

                if send_network_change(changes):

                    syslog.syslog(
                        "NetMonitor: network change notification sent"
                    )

                _save_notify_state({
                    "networks": current
                })

            elif previous != current:

                _save_notify_state({
                    "networks": current
                })

        except Exception as e:

            syslog.syslog(
                f"NetMonitor: network change monitor error: {e}"
            )

        time.sleep(
            NETWORK_CHECK_INTERVAL
        )



def start_network_change_monitor():

    thread = threading.Thread(
        target=_network_snapshot_loop,
        name="netmonitor-network-change",
        daemon=True
    )

    thread.start()

    return thread



def send_startup_notification():

    syslog.syslog(
        "NetMonitor: send_startup_notification() called"
    )

    connection = _ntfy_connection()

    if connection is None:

        syslog.syslog(
            "NetMonitor: startup notification unavailable"
        )

        return

    server, topic, token, ntfy = connection

    if not ntfy.get(
        "notify_startup",
        True
    ):

        syslog.syslog(
            "NetMonitor: startup notifications disabled"
        )

        return

    identity = get_watchdog_identity()
    current = identity["networks"]

    restart_reason = get_restart_reason()
    previous_state = _load_notify_state()
    previous = previous_state.get(
        "networks",
        []
    )

    changes = _network_changes(
        previous,
        current
    )

    for _ in range(30):

        try:

            if restart_reason:

                reason = restart_reason.get(
                    "reason",
                    "STARTED"
                )

                details = restart_reason.get(
                    "details",
                    ""
                )

                title = (
                    f"🐕 {identity['name']} — "
                    f"{reason.upper()}"
                )

                message = (
                    f"{details}\n\n"
                    "System restarted."
                    if details
                    else
                    "System restarted."
                )

            else:

                title = (
                    f"🐕 {identity['name']} — STARTED"
                )

                message = format_startup_message(
                    identity
                )

            success = send_ntfy(
                server,
                topic,
                token,
                title,
                message,
                tags="dog,computer",
                priority="default"
            )

            if success:

                syslog.syslog(
                    "NetMonitor: startup notification sent"
                )

                if restart_reason:

                    clear_restart_reason()

                break

        except Exception as e:

            syslog.syslog(
                f"NetMonitor: startup notification error: {e}"
            )

        time.sleep(2)

    else:

        syslog.syslog(
            "NetMonitor: startup notification "
            "failed after 60 seconds"
        )

    if changes:

        try:

            if send_network_change(changes):

                syslog.syslog(
                    "NetMonitor: startup network change notification sent"
                )

        except Exception as e:

            syslog.syslog(
                f"NetMonitor: startup network change notification error: {e}"
            )

    _save_notify_state({
        "networks": current
    })



def send_event_notification(
    job,
    state,
    duration
):

    if state == "DOWN":

        setting = "notify_incidents"
        event_label = "INCIDENT"
        tags = "rotating_light,warning"
        priority = "high"

    else:

        setting = "notify_recoveries"
        event_label = "RECOVERED"
        tags = "white_check_mark,heavy_check_mark"
        priority = "default"

    if not _notification_enabled(setting):

        return False

    connection = _ntfy_connection()

    if connection is None:

        return False

    server, topic, token, ntfy = connection
    identity = get_watchdog_identity()
    network = job.get(
        "network",
        {}
    )

    lines = [
        f"WATCHDOG {event_label}",
        "",
        f"Name: {identity['name']}",
        f"Location: {identity['location']}",
        f"Hostname: {identity['hostname']}",
        f"Version: {identity['version']}-{identity['build']}",
        "",
        f"Object: {job.get('name', 'Unknown')}",
        f"Type: {job.get('type', 'Unknown')}",
        f"State: {state}",
        f"Network: {network.get('name', 'Unknown')}",
        f"Interface: {network.get('interface', 'Unknown')}",
        f"Watchdog IP: {get_watchdog_ip_for_network(network)}",
        f"Gateway: {network.get('gateway', 'Unknown')}"
    ]

    if job.get("ip"):

        lines.append(
            f"Target IP: {job['ip']}"
        )

    if job.get("server"):

        lines.append(
            f"DNS Server: {job['server']}"
        )

    if job.get("targets"):

        lines.append(
            f"Internet Targets: {', '.join(job['targets'])}"
        )

    if duration is not None:

        lines.append(
            f"Outage Duration: {duration}s"
        )

    lines.extend([
        "",
        f"Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ])

    title = (
        f"{'🔴' if state == 'DOWN' else '🟢'} "
        f"{identity['name']} — {event_label}"
    )

    return send_ntfy(
        server,
        topic,
        token,
        title,
        "\n".join(lines),
        tags=tags,
        priority=priority
    )



def send_test_notification(
    server,
    topic,
    token,
    name
):

    if not name:

        name = "Watchdog"

    identity = get_watchdog_identity()
    identity["name"] = name

    return send_ntfy(
        server,
        topic,
        token,
        f"🧪 {name} — NTFY TEST",
        "\n".join([
            "WATCHDOG NTFY TEST",
            "",
            f"Name: {identity['name']}",
            f"Location: {identity['location']}",
            f"Hostname: {identity['hostname']}",
            f"Version: {identity['version']}-{identity['build']}",
            f"Tailscale IP: {identity['tailscale_ip'] or 'Not available'}",
            f"Devices monitored: {identity['device_count']}",
            "",
            "NETWORKS",
            *_format_network_lines(identity["networks"]),
            "",
            f"Tested: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]),
        tags="test_tube",
        priority="default"
    )
