#!/usr/bin/env python3

import subprocess

import dns.resolver


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


def dns_lookup(server, hostname):

    resolver = dns.resolver.Resolver(configure=False)

    resolver.nameservers = [server]

    resolver.timeout = 2
    resolver.lifetime = 2

    try:

        resolver.resolve(hostname, "A")

        return True

    except Exception:

        return False
