#!/bin/bash

require_root()
{
    if [[ $EUID -ne 0 ]]; then

        echo
        echo "This command requires administrator privileges."
        echo
        echo "Please run:"
        echo
        echo "    sudo $0 ${*:2}"
        echo

        exit 1
    fi
}
