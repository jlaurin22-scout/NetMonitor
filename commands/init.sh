#!/bin/bash

CONFIG="/etc/netmonitor/netmonitor.json"

echo
echo "========================================"
echo "       NetMonitor Setup Wizard"
echo "========================================"
echo

read -p "Customer Name : " CUSTOMER
read -p "Site          : " SITE

read -p "Static IP     : " IP
read -p "Prefix        : " PREFIX
read -p "Gateway       : " GATEWAY

read -p "DNS 1         : " DNS1
read -p "DNS 2         : " DNS2

DEVICE_JSON=""

while true
do
    echo
    read -p "Add Device (Y/N): " ANSWER

    if [[ "$ANSWER" != "Y" && "$ANSWER" != "y" ]]; then
        break
    fi

    echo
    read -p "Device Name : " DEVICENAME

    echo
    echo "Device Type"
    echo "-----------"
    echo "1) Internet Radio"
    echo "2) NAS"
    echo "3) Switch"
    echo "4) Printer"
    echo "5) Access Point"
    echo "6) Camera"
    echo "7) Server"
    echo "8) Workstation"
    echo "9) Other"
    echo

    read -p "Choice : " TYPE

    case "$TYPE" in
        1) DEVICETYPE="radio" ;;
        2) DEVICETYPE="nas" ;;
        3) DEVICETYPE="switch" ;;
        4) DEVICETYPE="printer" ;;
        5) DEVICETYPE="accesspoint" ;;
        6) DEVICETYPE="camera" ;;
        7) DEVICETYPE="server" ;;
        8) DEVICETYPE="workstation" ;;
        *) DEVICETYPE="other" ;;
    esac

    read -p "Device IP   : " DEVICEIP

    if [ -n "$DEVICE_JSON" ]; then
        DEVICE_JSON+=","
    fi

    DEVICE_JSON+="
        {
            \"name\": \"$DEVICENAME\",
            \"type\": \"$DEVICETYPE\",
            \"ip\": \"$DEVICEIP\"
        }"
done

cat > /tmp/netmonitor.json << EOF
{
    "version": "0.2.0",

    "customer": "$CUSTOMER",
    "site": "$SITE",

    "network": {
        "ip": "$IP",
        "prefix": $PREFIX,
        "gateway": "$GATEWAY",
        "dns": [
            "$DNS1",
            "$DNS2"
        ]
    },

    "devices": [
$DEVICE_JSON
    ],

    "tailscale": true
}
EOF

sudo mv /tmp/netmonitor.json "$CONFIG"

echo
echo "Configuration saved."
