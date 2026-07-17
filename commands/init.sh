#!/bin/bash

CONFIG="/etc/netmonitor/netmonitor.json"
SERVICE="netmonitor.service"

NETWORK_INFO=$(python3 <<'EOF'
import json
import sys

sys.path.insert(0, "/usr/local/lib/netmonitor/engine")

from inventory.network import detect

print(json.dumps(detect()))
EOF
)

INTERFACE=$(echo "$NETWORK_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['interface'])")
IP=$(echo "$NETWORK_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['ip'])")
PREFIX=$(echo "$NETWORK_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['prefix'])")
GATEWAY=$(echo "$NETWORK_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['gateway'])")
NETWORK=$(echo "$NETWORK_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['network'])")
DNS1=$(echo "$NETWORK_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['dns'][0])")
DNS2=$(echo "$NETWORK_INFO" | python3 -c "import sys,json; print(json.load(sys.stdin)['dns'][1])")

clear

echo
echo "========================================"
echo "       NetMonitor Setup Wizard"
echo "========================================"
echo

read -p "Customer Name : " CUSTOMER
read -p "Site          : " SITE

echo
echo "Detected Network"
echo "----------------"
echo "Interface : $INTERFACE"
echo "IP        : $IP"
echo "Prefix    : /$PREFIX"
echo "Gateway   : $GATEWAY"
echo "Network   : $NETWORK"
echo "DNS 1     : $DNS1"
echo "DNS 2     : $DNS2"
echo

read -p "Use these settings? (Y/N): " ANSWER

if [[ ! "$ANSWER" =~ ^[Yy]$ ]]; then
    echo
    echo "Setup cancelled."
    exit 0
fi

#
# Configure monitored devices
#
DEVICES_JSON=""

echo
echo "========================================"
echo " Configure Monitored Devices"
echo "========================================"

while true
do
    echo
    read -p "Add a monitored device? (Y/N): " ADDDEVICE

    if [[ ! "$ADDDEVICE" =~ ^[Yy]$ ]]; then
        break
    fi

    read -p "Device Name : " DEVICENAME
    read -p "IP Address  : " DEVICEIP

    read -p "Enable Ping monitoring? (Y/N): " PING
    read -p "Enable SNMP monitoring? (Y/N): " SNMP

    [[ "$PING" =~ ^[Yy]$ ]] && PING=true || PING=false
    [[ "$SNMP" =~ ^[Yy]$ ]] && SNMP=true || SNMP=false

    if [ -n "$DEVICES_JSON" ]; then
        DEVICES_JSON="${DEVICES_JSON},"
    fi

    DEVICES_JSON="${DEVICES_JSON}
        {
            \"id\": $(( $(echo "$DEVICES_JSON" | grep -c '"id"') + 1 )),
            \"name\": \"${DEVICENAME}\",
            \"ip\": \"${DEVICEIP}\",
            \"checks\": {
                \"ping\": ${PING},
                \"snmp\": ${SNMP}
            }
        }"
done

cat >/tmp/netmonitor.json <<EOF
{
    "version": "0.4.0",

    "customer": "$CUSTOMER",
    "site": "$SITE",

    "network": {
        "interface": "$INTERFACE",
        "ip": "$IP",
        "prefix": $PREFIX,
        "gateway": "$GATEWAY",
        "dns": [
            "$DNS1",
            "$DNS2"
        ]
    },

    "devices": [],

    "tailscale": true
}
EOF

mv /tmp/netmonitor.json "$CONFIG"

echo
echo "Initializing database..."

python3 <<EOF
import sys

sys.path.insert(0, "/usr/local/lib/netmonitor/engine")

from database import initialize

initialize()
EOF

#
# Give ownership to the service account
#
chown root:root /var/lib/netmonitor/netmonitor.db
chmod 664 /var/lib/netmonitor/netmonitor.db

echo "Database initialized."

echo
echo "Starting NetMonitor service..."

systemctl daemon-reload
systemctl enable "$SERVICE" >/dev/null 2>&1
systemctl restart "$SERVICE"

sleep 2

if systemctl is-active --quiet "$SERVICE"; then

    echo "Service started successfully."

else

    echo
    echo "ERROR: NetMonitor service failed to start."
    echo
    echo "Run:"
    echo
    echo "    systemctl status $SERVICE"
    echo
    exit 1

fi

echo
echo "NetMonitor is ready."
echo
echo "Run:"
echo
echo "    nm status"
echo
