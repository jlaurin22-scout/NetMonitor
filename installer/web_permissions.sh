#!/bin/bash

install_web_permissions()
{
    echo "Configuring Web GUI service permissions..."

    cat > /usr/local/sbin/netmonitor-web-restart << EOF
#!/bin/sh

exec /usr/bin/systemctl restart netmonitor
EOF

    chown root:root \
        /usr/local/sbin/netmonitor-web-restart

    chmod 755 \
        /usr/local/sbin/netmonitor-web-restart

    cat > /etc/sudoers.d/netmonitor-web << EOF
$WEB_USER ALL=(root) NOPASSWD: /usr/local/sbin/netmonitor-web-restart
EOF

    chown root:root \
        /etc/sudoers.d/netmonitor-web

    chmod 440 \
        /etc/sudoers.d/netmonitor-web

    visudo \
        -cf /etc/sudoers.d/netmonitor-web

    setfacl \
        -m u:$WEB_USER:--x \
        "$PROJECT_DIR"

    setfacl \
        -R \
        -m u:$WEB_USER:rx \
        "$PROJECT_DIR"

    echo "Web GUI service permissions configured."
    echo
}
