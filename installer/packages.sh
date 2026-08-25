#!/bin/bash

install_packages()
{
    echo "Installing required packages..."

    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-rich \
        python3-requests \
        python3-psutil \
        python3-dnspython \
        python3-pysnmp4 \
        python3-reportlab \
        python3-flask \
        gunicorn \
        ieee-data \
        samba-common-bin \
        avahi-utils \
        iputils-ping \
        dnsutils \
        net-tools \
        iproute2 \
        acl \
        curl

    echo
    echo "Package installation complete."
    echo
}