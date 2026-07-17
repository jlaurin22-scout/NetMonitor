#!/usr/bin/env python3

import socket
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


def dns_server_reachable(server):

    return ping(server)

def dns_lookup(server, hostname):

    try:

        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [server]
        resolver.timeout = 2
        resolver.lifetime = 2

        answer = resolver.resolve(hostname)

        return True, f"Resolved in {answer.response.time * 1000:.0f} ms"

    except dns.resolver.LifetimeTimeout:

        return False, "DNS query timed out"

    except dns.resolver.NXDOMAIN:

        return False, "Host does not exist"

    except dns.resolver.NoNameservers:

        return False, "No DNS server available"

    except Exception as e:

        return False, str(e)
