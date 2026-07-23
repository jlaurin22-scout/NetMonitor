#!/usr/bin/env python3

import syslog
import socket
import subprocess
import time

TOPIC = "stiel-scout"


def send_startup_ip():

    syslog.syslog("NetMonitor: send_startup_ip() called")

    for _ in range(30):  # Try for up to 60 seconds

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("1.1.1.1", 80))
            ip = s.getsockname()[0]
            s.close()

            result = subprocess.run(
                [
                    "curl",
                    "-s",
                    "-d",
                    ip,
                    f"https://ntfy.sh/{TOPIC}"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )

            if result.returncode == 0:
                syslog.syslog("NetMonitor: startup notification sent")
                return

        except Exception:
            pass

        time.sleep(2)

    syslog.syslog("NetMonitor: startup notification failed after 60 seconds")
