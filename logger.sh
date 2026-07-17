#!/bin/bash

LOGFILE="/var/log/netmonitor/netmonitor.log"

log() {

    local LEVEL="$1"
    local MESSAGE="$2"

    printf "%s [%s] %s\n" \
        "$(date '+%Y-%m-%d %H:%M:%S')" \
        "$LEVEL" \
        "$MESSAGE" >> "$LOGFILE"
}
