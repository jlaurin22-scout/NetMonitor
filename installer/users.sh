#!/bin/bash

install_users()
{
    echo "Creating NetMonitor service accounts..."

    if ! getent group "$NETMONITOR_GROUP" >/dev/null 2>&1; then

        groupadd \
            --system \
            "$NETMONITOR_GROUP"

        echo "Created group: $NETMONITOR_GROUP"

    else

        echo "Group already exists: $NETMONITOR_GROUP"

    fi

    if ! id "$WEB_USER" >/dev/null 2>&1; then

        useradd \
            --system \
            --no-create-home \
            --shell /usr/sbin/nologin \
            --gid "$NETMONITOR_GROUP" \
            "$WEB_USER"

        echo "Created user: $WEB_USER"

    else

        echo "User already exists: $WEB_USER"

    fi

    usermod \
        --gid "$NETMONITOR_GROUP" \
        "$WEB_USER"

    echo
    echo "NetMonitor service accounts ready."
    echo
}
