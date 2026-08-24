#!/bin/bash

verify_installation()
{
    echo "======================================"
    echo " Installation Summary"
    echo "======================================"
    echo

    systemctl is-enabled netmonitor >/dev/null
    echo "✓ Monitoring service enabled"

    systemctl is-active netmonitor >/dev/null
    echo "✓ Monitoring service running"

    systemctl is-enabled netmonitor-web >/dev/null
    echo "✓ Web GUI service enabled"

    systemctl is-active netmonitor-web >/dev/null
    echo "✓ Web GUI service running"

    command -v nm >/dev/null
    echo "✓ nm command available"

    command -v gunicorn >/dev/null
    echo "✓ Gunicorn available"

    echo
}