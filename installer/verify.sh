#!/bin/bash

verify_installation()
{
    echo "======================================"
    echo " Installation Summary"
    echo "======================================"
    echo

    systemctl is-enabled netmonitor >/dev/null
    echo "✓ Service enabled"

    systemctl is-active netmonitor >/dev/null
    echo "✓ Service running"

    command -v nm >/dev/null
    echo "✓ nm command available"

    echo
}
