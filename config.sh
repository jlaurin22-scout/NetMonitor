#!/bin/bash

CONFIG="/etc/netmonitor/netmonitor.json"

load_config() {

    if [ ! -f "$CONFIG" ]; then
        echo "Configuration file not found."
        exit 1
    fi

    VERSION=$(jq -r '.version' "$CONFIG")

    CUSTOMER=$(jq -r '.customer' "$CONFIG")
    SITE=$(jq -r '.site' "$CONFIG")

    IP=$(jq -r '.network.ip' "$CONFIG")
    PREFIX=$(jq -r '.network.prefix' "$CONFIG")
    GATEWAY=$(jq -r '.network.gateway' "$CONFIG")

    DNS1=$(jq -r '.network.dns[0]' "$CONFIG")
    DNS2=$(jq -r '.network.dns[1]' "$CONFIG")
}
