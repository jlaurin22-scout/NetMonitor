#!/usr/bin/env python3

import ipaddress
import subprocess

import dns.resolver


TABLE_BASE = 10000
PRIORITY_BASE = 10000


def setup_network_routes(networks):

    configured = []

    for network in networks:

        table = TABLE_BASE + int(network["id"])
        priority = PRIORITY_BASE + int(network["id"])

        interface = network["interface"]
        ip = network["ip"]
        prefix = network["prefix"]
        gateway = network["gateway"]

        network_address = str(
            ipaddress.ip_network(
                f"{ip}/{prefix}",
                strict=False
            ).network_address
        )

        subprocess.run(
            [
                "ip",
                "rule",
                "del",
                "priority",
                str(priority)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        subprocess.run(
            [
                "ip",
                "route",
                "flush",
                "table",
                str(table)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        result = subprocess.run(
            [
                "ip",
                "route",
                "add",
                f"{network_address}/{prefix}",
                "dev",
                interface,
                "src",
                ip,
                "table",
                str(table)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            raise RuntimeError(
                f"Unable to configure route "
                f"for network {network['id']}: "
                f"{result.stderr.strip()}"
            )

        result = subprocess.run(
            [
                "ip",
                "route",
                "add",
                "default",
                "via",
                gateway,
                "dev",
                interface,
                "table",
                str(table)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            raise RuntimeError(
                f"Unable to configure gateway "
                f"{gateway} for network {network['id']}: "
                f"{result.stderr.strip()}"
            )

        result = subprocess.run(
            [
                "ip",
                "rule",
                "add",
                "priority",
                str(priority),
                "from",
                f"{ip}/32",
                "table",
                str(table)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            raise RuntimeError(
                f"Unable to configure routing policy "
                f"for network {network['id']}: "
                f"{result.stderr.strip()}"
            )

        configured.append(
            (table, priority)
        )

    return configured


def cleanup_network_routes(networks):

    for network in networks:

        table = TABLE_BASE + int(network["id"])
        priority = PRIORITY_BASE + int(network["id"])

        subprocess.run(
            [
                "ip",
                "rule",
                "del",
                "priority",
                str(priority)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        subprocess.run(
            [
                "ip",
                "route",
                "flush",
                "table",
                str(table)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


def ping(host, network=None):

    command = [
        "ping",
        "-c",
        "1",
        "-W",
        "1"
    ]

    if network is not None:

        command.extend(
            [
                "-I",
                network["ip"]
            ]
        )

    command.append(host)

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def dns_lookup(server, hostname, network=None):

    resolver = dns.resolver.Resolver(
        configure=False
    )

    resolver.nameservers = [
        server
    ]

    resolver.timeout = 2
    resolver.lifetime = 2

    try:

        if network is None:

            resolver.resolve(
                hostname,
                "A"
            )

            return True

        source_ip = network["ip"]

        result = subprocess.run(
            [
                "dig",
                "+time=2",
                "+tries=1",
                f"@{server}",
                hostname,
                "A",
                "-b",
                source_ip
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return result.returncode == 0

    except Exception:

        return False