#!/usr/bin/env python3

FINGERPRINTS = [

    #
    # Firewalls
    #

    {
        "type": "Firewall",
        "http_server": "opnsense",
    },

    {
        "type": "Firewall",
        "http_title": "login | opnsense",
    },

    #
    # Routers
    #

    {
        "type": "Telekom DIGI Box",
        "vendor": "elmegt",
        "http_server": "boss",
    },

    {
        "type": "Router",
        "vendor": "avm",
    },

    #
    # Mail
    #

    {
        "type": "Mail Gateway",
        "http_title": "securepoint uma",
    },

    #
    # Servers
    #

    {
        "type": "Windows Server",
        "http_server": "microsoft-iis",
    },

    {
        "type": "Linux Server",
        "http_server": "apache",
        "http_title": "ubuntu",
    },

    #
    # Storage
    #

    {
        "type": "NAS",
        "vendor": "qnap",
    },

    #
    # Printers
    #

    {
        "type": "Printer",
        "http_server": "canon http server",
    },

    {
        "type": "Printer",
        "http_server": "epson_linux",
    },

    #
    # Infrastructure
    #

    {
        "type": "Powerline",
        "vendor": "devolo",
    },

    {
        "type": "Switch",
        "vendor": "d-link",
    },

    #
    # Hostname fingerprints
    #

    {
        "type": "Firewall",
        "hostname": "opnsense",
    },

    {
        "type": "Windows Server",
        "hostname": "srv",
    },

    {
        "type": "Camera",
        "hostname": "kamera",
    },

    {
        "type": "Switch",
        "hostname": "switch",
    },

    {
        "type": "Printer",
        "hostname": "printer",
    },

    {
        "type": "Powerline",
        "hostname": "devolo",
    },

    {
        "type": "Pi-hole",
        "hostname": "pihole",
    },

    {
        "type": "NetMonitor",
        "hostname": "net-monitor",
    },

    {
        "type": "Watchdog",
        "hostname": "watchdog",
    },

    {
        "type": "Linux Miner",
        "hostname": "miner",
    },
]