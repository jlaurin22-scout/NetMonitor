#!/bin/bash

restart_service()
{
    echo "Restarting Scout..."

    systemctl restart netmonitor

    echo "Scout restarted."
    echo
}
