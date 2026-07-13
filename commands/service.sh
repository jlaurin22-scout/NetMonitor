#!/bin/bash

SERVICE="netmonitor.service"

clear

GREEN="\033[32m"
RED="\033[31m"
RESET="\033[0m"

ACTIVE=$(systemctl is-active "$SERVICE")
ENABLED=$(systemctl is-enabled "$SERVICE" 2>/dev/null)

PID=$(systemctl show "$SERVICE" -p MainPID --value)
UPTIME=$(systemctl show "$SERVICE" -p ActiveEnterTimestamp --value)

echo
echo "=========================================================="
echo "                NetMonitor Service"
echo "=========================================================="
echo

if [ "$ACTIVE" = "active" ]; then
    printf "Status      : ${GREEN}● Running${RESET}\n"
else
    printf "Status      : ${RED}● Stopped${RESET}\n"
fi

echo "Startup     : $ENABLED"
echo "PID         : $PID"
echo "Started     : $UPTIME"

echo
