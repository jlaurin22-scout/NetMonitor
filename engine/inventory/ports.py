#!/usr/bin/env python3

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


PORTS = [
    22,
    53,
    80,
    443,
    445,
    515,
    631,
    9100,
    3389,
    161,
]


def check(ip, port, timeout=0.2):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        return port if sock.connect_ex((ip, port)) == 0 else None

    except Exception:
        return None

    finally:
        sock.close()


def scan(ip):

    open_ports = []

    with ThreadPoolExecutor(max_workers=10) as pool:

        futures = {
            pool.submit(check, ip, port): port
            for port in PORTS
        }

        for future in as_completed(futures):

            port = future.result()

            if port is not None:
                open_ports.append(port)

    open_ports.sort()

    return open_ports


def enrich(device):

    device.ports = scan(device.ip)


if __name__ == "__main__":

    while True:

        ip = input("IP: ").strip()

        if not ip:
            break

        print(scan(ip))
