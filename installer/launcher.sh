#!/bin/bash

install_launcher()
{
    echo "Installing launcher..."

    cat > "$BIN_DIR/nm" << EOF
#!/bin/bash

cd "$PROJECT_DIR"

if [ "\$EUID" -ne 0 ]; then
    exec sudo python3 cli.py "\$@"
fi

exec python3 cli.py "\$@"
EOF

    chmod 755 "$BIN_DIR/nm"

    echo "Launcher installed."
    echo
}
