#!/bin/bash

create_directories()
{
    echo "Creating directories..."

    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$DATA_DIR/reports"

    chown -R "$INSTALL_USER:$INSTALL_GROUP" "$DATA_DIR"

    echo "Directories created."
    echo
}