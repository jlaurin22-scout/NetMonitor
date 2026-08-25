#!/bin/bash

install_service()
{
    echo "Installing systemd services..."

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

    cat > "$SERVICE_DIR/netmonitor-web.service" << EOF
[Unit]
Description=Scout Network Monitor Web GUI
After=network-online.target netmonitor.service
Wants=network-online.target

[Service]
Type=simple
User=$WEB_USER
Group=$NETMONITOR_GROUP
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/gunicorn --bind 0.0.0.0:8080 --workers 1 --access-logfile - --error-logfile - web.app:app
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload

    systemctl enable netmonitor
    systemctl enable netmonitor-web

    echo "Systemd services installed."
    echo
}