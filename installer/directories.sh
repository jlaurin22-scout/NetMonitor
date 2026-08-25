#!/bin/bash

create_directories()
{
    echo "Creating directories..."

    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$DATA_DIR/reports"

    chown -R "$INSTALL_USER:$INSTALL_GROUP" "$PROJECT_DIR"

    chown root:"$NETMONITOR_GROUP" "$CONFIG_DIR"
    chmod 750 "$CONFIG_DIR"

    chown root:"$NETMONITOR_GROUP" "$DATA_DIR"
    chmod 770 "$DATA_DIR"

    if [ -f "$CONFIG_DIR/netmonitor.json" ]; then

        chown root:"$NETMONITOR_GROUP" \
            "$CONFIG_DIR/netmonitor.json"

        chmod 660 \
            "$CONFIG_DIR/netmonitor.json"

    fi

    if [ -f "$CONFIG_DIR/devices.json" ]; then

        chown root:"$NETMONITOR_GROUP" \
            "$CONFIG_DIR/devices.json"

        chmod 660 \
            "$CONFIG_DIR/devices.json"

    fi

    if [ -f "$CONFIG_DIR/settings.json" ]; then

        chown root:"$NETMONITOR_GROUP" \
            "$CONFIG_DIR/settings.json"

        chmod 660 \
            "$CONFIG_DIR/settings.json"

    fi

    if [ -f "$CONFIG_DIR/devices.json.backup" ]; then

        chown root:"$NETMONITOR_GROUP" \
            "$CONFIG_DIR/devices.json.backup"

        chmod 660 \
            "$CONFIG_DIR/devices.json.backup"

    fi

    if [ -f "$DATA_DIR/netmonitor.db" ]; then

        chown root:"$NETMONITOR_GROUP" \
            "$DATA_DIR/netmonitor.db"

        chmod 660 \
            "$DATA_DIR/netmonitor.db"

    fi

    echo "Directories created."
    echo
}