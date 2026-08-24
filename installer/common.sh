#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

BIN_DIR="/usr/local/bin"
CONFIG_DIR="/etc/netmonitor"
DATA_DIR="/var/lib/netmonitor"
SERVICE_DIR="/etc/systemd/system"

#
# Determine the user who launched the installer.
#
# When started with sudo, SUDO_USER contains the
# original non-root user. If SUDO_USER is not set,
# fall back to the owner of the project directory.
#

if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then

    INSTALL_USER="$SUDO_USER"

else

    INSTALL_USER="$(stat -c '%U' "$PROJECT_DIR")"

fi

INSTALL_GROUP="$(id -gn "$INSTALL_USER")"


print_header()
{
    echo
    echo "======================================"
    echo " Scout Network Monitor Installer"
    echo "======================================"
    echo
}


require_root()
{
    if [ "$EUID" -ne 0 ]; then
        echo "Please run this installer with sudo."
        exit 1
    fi
}


select_installation_type()
{
    echo "Select installation type:"
    echo
    echo "  1) New installation"
    echo "  2) Update existing installation"
    echo

    while true; do

        read -r -p "Selection [1/2]: " INSTALL_TYPE

        case "$INSTALL_TYPE" in

            1)
                echo
                echo "WARNING: New installation will remove the existing"
                echo "NetMonitor configuration and monitoring database."
                echo

                read -r -p "Continue with new installation? [y/N]: " ANSWER

                case "$ANSWER" in
                    y|Y|yes|YES|Yes)
                        INSTALL_MODE="new"
                        return
                        ;;
                    *)
                        echo
                        echo "Installation cancelled."
                        exit 0
                        ;;
                esac
                ;;

            2)
                INSTALL_MODE="update"
                return
                ;;

            *)
                echo "Please enter 1 or 2."
                echo
                ;;

        esac

    done
}


prepare_installation()
{
    if [ "$INSTALL_MODE" = "new" ]; then

        echo "Preparing new installation..."

        systemctl stop netmonitor 2>/dev/null || true

        rm -rf "$CONFIG_DIR"
        rm -f "$DATA_DIR/netmonitor.db"

        echo "Existing configuration and database removed."
        echo

    else

        echo "Preparing update..."

        echo "Existing configuration and database will be preserved."
        echo

    fi
}
