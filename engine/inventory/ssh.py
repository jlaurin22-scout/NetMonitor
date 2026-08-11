#!/usr/bin/env python3

import socket


def enrich(device):
    """
    Read the SSH banner without logging in.
    """

    if 22 not in device.ports:
        return

    try:

        sock = socket.create_connection(
            (device.ip, 22),
            timeout=2
        )

        sock.settimeout(2)

        banner = sock.recv(256).decode(
            "utf-8",
            errors="ignore"
        ).strip()

        sock.close()

        device.ssh_banner = banner

    except Exception:

        pass


if __name__ == "__main__":

    from device import Device

    d = Device("127.0.0.1")
    d.ports = [22]

    enrich(d)

    print(d.ssh_banner)