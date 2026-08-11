#!/usr/bin/env python3

import socket
import ssl


def probe(ip, port):

    try:

        if port == 443:

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            sock = context.wrap_socket(
                socket.socket(socket.AF_INET),
                server_hostname=ip
            )

        else:

            sock = socket.socket(socket.AF_INET)

        sock.settimeout(3)

        sock.connect((ip, port))

        request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {ip}\r\n"
            f"Connection: close\r\n\r\n"
        )

        sock.send(request.encode())

        response = sock.recv(8192).decode(
            errors="ignore"
        )

        sock.close()

        return response

    except Exception:

        return ""


def enrich(device):

    device.http_server = ""
    device.http_title = ""

    port = None

    if 443 in device.ports:

        port = 443

    elif 80 in device.ports:

        port = 80

    else:

        return

    response = probe(
        device.ip,
        port
    )

    if not response:

        return

    for line in response.splitlines():

        if line.lower().startswith("server:"):

            device.http_server = line.split(
                ":",
                1
            )[1].strip()

            break

    lower = response.lower()

    start = lower.find("<title>")
    end = lower.find("</title>")

    if (
        start != -1
        and
        end != -1
        and
        end > start
    ):

        device.http_title = response[
            start + 7:end
        ].strip()