#!/bin/bash

DB="/var/lib/netmonitor/netmonitor.db"

clear

echo
echo "=========================================================="
echo "                 NetMonitor Health"
echo "=========================================================="
echo

SERVICE=$(systemctl is-active netmonitor.service)

if [ "$SERVICE" = "active" ]; then
    echo "Service      : OK"
else
    echo "Service      : FAILED"
fi

if [ -f "$DB" ]; then
    echo "Database     : OK"
else
    echo "Database     : FAILED"
fi

TAILSCALE=$(tailscale status >/dev/null 2>&1; echo $?)

if [ "$TAILSCALE" = "0" ]; then
    echo "Tailscale    : Connected"
else
    echo "Tailscale    : Disconnected"
fi

echo

sqlite3 "$DB" <<EOF
SELECT
    printf('%-12s : %s', job_name, state)
FROM current_status;
EOF

echo
