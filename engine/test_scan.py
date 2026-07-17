from inventory.network import detect
from discovery.scan import scan_network

info = detect()

print("Network information")
print("-------------------")
print(f"IP      : {info['ip']}")
print(f"Gateway : {info['gateway']}")
print(f"Network : {info['network']}")

print("\nScanning...")

hosts = scan_network(info["network"])

print(f"\nFound {len(hosts)} active devices:\n")

for host in hosts:
    print(host)
