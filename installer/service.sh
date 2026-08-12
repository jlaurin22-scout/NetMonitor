#!/bin/bash

install_service()
{
    echo "Installing systemd service..."

    cat > "$SERVICE_DIR/netmonitor.service" << EOF
[Unit]
Description=Scout Network Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 -m engine.main
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable netmonitor

    echo "Systemd service installed."
    echo
}
