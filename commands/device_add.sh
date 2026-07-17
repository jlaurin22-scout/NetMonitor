#!/bin/bash

clear

echo
echo "========================================"
echo "      Add Monitored Device"
echo "========================================"
echo

read -p "Device Name : " NAME
read -p "IP Address  : " IP

echo

read -p "Enable Ping monitoring? (Y/N): " PING
read -p "Enable SNMP monitoring? (Y/N): " SNMP

if [[ "$PING" =~ ^[Yy]$ ]]; then
    PING=True
else
    PING=False
fi

if [[ "$SNMP" =~ ^[Yy]$ ]]; then
    SNMP=True
else
    SNMP=False
fi

python3 <<EOF
import sys

sys.path.insert(0, "/usr/local/lib/netmonitor/engine")

import config

try:
    config.add_device(
        name="$NAME",
        ip="$IP",
        ping=$PING,
        snmp=$SNMP
    )

    print()
    print("Device added successfully.")

except Exception as e:
    print()
    print(f"ERROR: {e}")
EOF

echo
