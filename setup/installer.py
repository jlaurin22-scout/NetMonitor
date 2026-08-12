#!/usr/bin/env python3

import subprocess
from pathlib import Path

from engine import database


PROJECT_DIR = Path(__file__).resolve().parent.parent

SERVICE = f"""[Unit]
Description=Scout Network Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory={PROJECT_DIR}
ExecStart=/usr/bin/python3 -m engine.main
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""


def run():

    Path(
        "/var/lib/netmonitor"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    database.initialize()

    Path(
        "/etc/systemd/system/netmonitor.service"
    ).write_text(SERVICE)

    subprocess.run(
        ["systemctl", "daemon-reload"],
        check=True
    )

    subprocess.run(
        ["systemctl", "enable", "netmonitor"],
        check=True
    )

    subprocess.run(
        ["systemctl", "restart", "netmonitor"],
        check=True
    )
