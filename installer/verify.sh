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

    id "$WEB_USER" >/dev/null
    echo "✓ Web GUI service account available"

    getent group "$NETMONITOR_GROUP" >/dev/null
    echo "✓ NetMonitor service group available"

    test -x /usr/local/sbin/netmonitor-web-restart
    echo "✓ Web restart helper available"

    test -f /etc/sudoers.d/netmonitor-web
    echo "✓ Web restart sudo policy available"

    visudo -cf /etc/sudoers.d/netmonitor-web >/dev/null
    echo "✓ Web restart sudo policy valid"

    sudo -u "$WEB_USER" \
        sudo -n \
        /usr/local/sbin/netmonitor-web-restart

    echo "✓ Web service can restart monitoring service"

    test -d "$CONFIG_DIR"
    echo "✓ Configuration directory available"

    test -d "$DATA_DIR"
    echo "✓ Data directory available"

    sudo -u "$WEB_USER" \
        test -r "$CONFIG_DIR/devices.json"

    echo "✓ Web service can read device configuration"

    sudo -u "$WEB_USER" \
        test -w "$CONFIG_DIR/devices.json"

    echo "✓ Web service can write device configuration"

    sudo -u "$WEB_USER" \
        test -r "$DATA_DIR/netmonitor.db"

    echo "✓ Web service can read monitoring database"

    sudo -u "$WEB_USER" \
        test -w "$DATA_DIR/netmonitor.db"

    echo "✓ Web service can write monitoring database"

    command -v nm >/dev/null
    echo "✓ nm command available"

    command -v gunicorn >/dev/null
    echo "✓ Gunicorn available"

    echo
    echo "Installation verification complete."
    echo
}