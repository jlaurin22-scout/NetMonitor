#!/usr/bin/env python3

import socket
import subprocess


def ping(host):

    result = subprocess.run(
        [
            "ping",
            "-c", "1",
            "-W", "1",
            host
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def dns_server_reachable(server):

    return ping(server)


def dns_lookup(hostname):

    try:

        socket.gethostbyname(hostname)

        return True

    except Exception:

        return False
