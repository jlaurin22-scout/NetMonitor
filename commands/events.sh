#!/bin/bash

DB="/var/lib/netmonitor/netmonitor.db"

echo
echo "==============================================="
echo "            Recent Events"
echo "==============================================="
echo

sqlite3 -header -column "$DB" <<EOF
SELECT
    timestamp,
    job_name,
    state,
    message
FROM events
ORDER BY id DESC
LIMIT 20;
EOF

echo
