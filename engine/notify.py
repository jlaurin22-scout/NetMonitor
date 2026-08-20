#!/usr/bin/env python3

import socket
import subprocess
import syslog
import time

from engine import config


def get_notification_ip():

    networks = config.get_networks()

    if networks:

        networks = sorted(
            networks,
            key=lambda network: network.get("id", 999999)
        )

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


def send_ntfy(
    server,
    topic,
    token,
    title,
    message
):

    url = (
        f"{server.rstrip('/')}/"
        f"{topic}"
    )

    command = [
        "curl",
        "-s",
        "-o",
        "/dev/null",
        "-w",
        "%{http_code}",
        "-X",
        "POST",
        "-H",
        f"Title: {title}",
        "-d",
        message,
        url
    ]

    if token:

        command.extend(
            [
                "-H",
                f"Authorization: Bearer {token}"
            ]
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


def send_startup_ip():

    syslog.syslog(
        "NetMonitor: send_startup_ip() called"
    )

    settings = config.load_settings()

    ntfy = settings.get(
        "ntfy",
        {}
    )

    if not ntfy.get(
        "enabled",
        False
    ):

        syslog.syslog(
            "NetMonitor: NTFY notifications disabled"
        )

        return

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

    name = ntfy.get(
        "name",
        ""
    ).strip()

    if not server:

        syslog.syslog(
            "NetMonitor: NTFY server not configured"
        )

        return

    if not topic:

        syslog.syslog(
            "NetMonitor: NTFY topic not configured"
        )

        return

    if not name:

        name = "Scout"

    for _ in range(30):

        try:

            ip = get_notification_ip()

            success = send_ntfy(
                server,
                topic,
                token,
                name,
                f"IP Address: {ip}"
            )

            if success:

                syslog.syslog(
                    "NetMonitor: startup notification sent"
                )

                return

        except Exception as e:

            syslog.syslog(
                f"NetMonitor: startup notification error: {e}"
            )

        time.sleep(2)

    syslog.syslog(
        "NetMonitor: startup notification "
        "failed after 60 seconds"
    )
