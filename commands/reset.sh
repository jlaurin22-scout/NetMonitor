#!/bin/bash

SERVICE="netmonitor.service"

if [ "$EUID" -ne 0 ]; then
    echo
    echo "This command must be run as root."
    echo
    echo "Please run:"
    echo "    sudo nm reset"
    echo
    exit 1
fi

clear

echo
echo "========================================"
echo "         NetMonitor Reset"
echo "========================================"
echo
echo "This will remove:"
echo
echo "  - Customer configuration"
echo "  - Monitoring database"
echo "  - State information"
echo "  - History"
echo "  - Log files"
echo
echo "NetMonitor will remain installed."
echo

read -p "Continue? (Y/N): " ANSWER

if [[ ! "$ANSWER" =~ ^[Yy]$ ]]; then
    echo
    echo "Reset cancelled."
    echo
    exit 0
fi

echo
echo "Stopping NetMonitor service..."

if systemctl list-unit-files | grep -q "^${SERVICE}"; then
    systemctl stop "$SERVICE"

    if systemctl is-active --quiet "$SERVICE"; then
        echo "FAILED to stop service."
        exit 1
    fi

    echo "Service stopped."
else
    echo "Service not installed."
fi

ERROR=0

remove_file() {

    if [ -e "$1" ]; then

        rm -f "$1"

        if [ $? -eq 0 ]; then
            printf "  [OK]     %s\n" "$1"
        else
            printf "  [FAILED] %s\n" "$1"
            ERROR=1
        fi

    else

        printf "  [SKIP]   %s (not found)\n" "$1"

    fi
}

remove_directory() {

    if [ -d "$1" ]; then

        rm -rf "$1"/*

        if [ $? -eq 0 ]; then
            printf "  [OK]     %s\n" "$1"
        else
            printf "  [FAILED] %s\n" "$1"
            ERROR=1
        fi

    else

        printf "  [SKIP]   %s (not found)\n" "$1"

    fi
}

echo
echo "Removing customer data..."
echo

remove_file "/etc/netmonitor/netmonitor.json"
remove_file "/var/lib/netmonitor/netmonitor.db"

remove_directory "/var/lib/netmonitor/state"
remove_directory "/var/lib/netmonitor/history"
remove_directory "/var/log/netmonitor"

echo

if [ "$ERROR" -eq 0 ]; then

    echo "Reset completed successfully."
    echo
    echo "The appliance is ready for a new customer."
    echo
    echo "Run:"
    echo "    sudo nm init"
    echo

else

    echo "Reset completed with errors."
    echo
    echo "Please review the messages above."
    echo
    exit 1

fi
