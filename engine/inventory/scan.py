#!/usr/bin/env python3

import ipaddress
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def ping(ip):
    """
    Ping a host once.

    Returns:
        (alive, response_time)
    """

    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", str(ip)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return False, None

    match = re.search(r"time=([0-9.]+)", result.stdout)

    if match:
        return True, float(match.group(1))

    return True, None


def scan_network(network):

    net = ipaddress.ip_network(network, strict=False)

    devices = []

    with ThreadPoolExecutor(max_workers=100) as pool:

        futures = {
            pool.submit(ping, ip): ip
            for ip in net.hosts()
        }

        for future in as_completed(futures):

            ip = futures[future]

            try:
                alive, response = future.result()

                if alive:
                    devices.append({
                        "ip": ip,
                        "response": response
                    })

            except Exception:
                pass

    devices.sort(key=lambda d: d["ip"])

    return [
        {
            "ip": str(device["ip"]),
            "response": device["response"]
        }
        for device in devices
    ]
