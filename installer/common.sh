#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

BIN_DIR="/usr/local/bin"
CONFIG_DIR="/etc/netmonitor"
DATA_DIR="/var/lib/netmonitor"
SERVICE_DIR="/etc/systemd/system"

print_header()
{
    echo
    echo "======================================"
    echo " Scout Network Monitor Installer"
    echo "======================================"
    echo
}

require_root()
{
    if [ "$EUID" -ne 0 ]; then
        echo "Please run this installer with sudo."
        exit 1
    fi
}
