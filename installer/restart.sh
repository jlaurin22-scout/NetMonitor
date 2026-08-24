#!/bin/bash

restart_service()
{
    echo "Restarting Scout services..."

    systemctl restart netmonitor
    systemctl restart netmonitor-web

    echo "Scout services restarted."
    echo
}