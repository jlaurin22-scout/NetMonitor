#!/bin/bash

DB="/var/lib/netmonitor/netmonitor.db"

GREEN="\033[32m"
RED="\033[31m"
RESET="\033[0m"

clear

echo
echo "=========================================================="
echo "                 NetMonitor Status"
echo "=========================================================="
echo

sqlite3 "$DB" <<EOF |
SELECT job_name, job_type, state, last_change
FROM current_status
ORDER BY
CASE job_type
    WHEN 'gateway' THEN 1
    WHEN 'internet' THEN 2
    WHEN 'dns' THEN 3
    ELSE 4
END,
job_name;
EOF

while IFS="|" read NAME TYPE STATUS LAST
do

    if [ "$STATUS" = "UP" ]; then
        ICON="${GREEN}●${RESET}"
    else
        ICON="${RED}●${RESET}"
    fi

    printf "%-18s %-10s %b %-5s %s\n" \
        "$NAME" \
        "($TYPE)" \
        "$ICON" \
        "$STATUS" \
        "$LAST"

done

echo
