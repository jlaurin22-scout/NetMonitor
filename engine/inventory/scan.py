import ipaddress
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def ping(ip):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", str(ip)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def scan_network(network):
    """
    Scan a network and return a list of responding hosts.

    Example:
        ['192.168.1.1',
         '192.168.1.15',
         '192.168.1.27']
    """

    net = ipaddress.ip_network(network, strict=False)

    alive = []

    with ThreadPoolExecutor(max_workers=100) as pool:

        futures = {
            pool.submit(ping, ip): str(ip)
            for ip in net.hosts()
        }

        for future in as_completed(futures):

            ip = futures[future]

            try:
                if future.result():
                    alive.append(ip)
            except Exception:
                pass

    return sorted(alive)
