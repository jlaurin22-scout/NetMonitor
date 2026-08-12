#!/bin/bash

install_packages()
{
    echo "Installing required packages..."

    apt update

    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-rich \
        python3-requests \
        python3-psutil \
        iputils-ping \
        dnsutils \
        net-tools \
        iproute2 \
        curl

    echo
    echo "Package installation complete."
}
