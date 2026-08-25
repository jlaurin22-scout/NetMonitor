#!/bin/bash

install_authentication()
{
    echo "Initializing Web GUI authentication..."
    echo

    if [ ! -f "$DATA_DIR/web.db" ]; then

        sudo -u "$WEB_USER" \
            /usr/bin/python3 -m web.auth_cli

    else

        echo "Existing Web GUI authentication database preserved."
        echo

    fi
}