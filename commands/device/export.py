#!/usr/bin/env python3

"""
Export a live NetMonitor discovery scan to a versioned CSV file.

This exports discovery observations only. It does not export configured
monitoring devices, configuration files, credentials, or monitoring history.
"""

import argparse
import csv
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = "1.0"

CSV_FIELDS = [
    "schema_version",
    "export_id",
    "exported_at_utc",
    "export_source",
    "ip_address",
    "mac_address",
    "hostname",
    "vendor",
    "device_type",
    "response_ms",
    "network_id",
    "dns_servers",
    "open_tcp_ports",
    "http_server",
    "http_title",
    "http_protocol",
    "ssh_banner",
    "snmp_enabled",
    "snmp_description",
    "snmp_uptime",
    "snmp_contact",
    "snmp_location",
    "model",
    "firmware",
    "serial",
]


def _joined(value):
    """Convert list-like values into a stable, readable CSV cell."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return ";".join(str(item) for item in value if item is not None)
    return str(value)


def _text(value):
    """Return a text value suitable for a plain CSV cell."""
    if value is None:
        return ""
    return str(value)


def _response_ms(value):
    if value is None:
        return ""
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return ""


def _device_row(device, export_id, exported_at):
    return {
        "schema_version": SCHEMA_VERSION,
        "export_id": export_id,
        "exported_at_utc": exported_at,
        "export_source": "netmonitor_live_scan",
        "ip_address": _text(getattr(device, "ip", "")),
        "mac_address": _text(getattr(device, "mac", "")),
        "hostname": _text(getattr(device, "hostname", "")),
        "vendor": _text(getattr(device, "vendor", "")),
        "device_type": _text(getattr(device, "device_type", "")),
        "response_ms": _response_ms(getattr(device, "response", None)),
        "network_id": _text(getattr(device, "network_id", "")),
        "dns_servers": _joined(getattr(device, "dns_servers", [])),
        "open_tcp_ports": _joined(getattr(device, "ports", [])),
        "http_server": _text(getattr(device, "http_server", "")),
        "http_title": _text(getattr(device, "http_title", "")),
        "http_protocol": _text(getattr(device, "http_protocol", "")),
        "ssh_banner": _text(getattr(device, "ssh_banner", "")),
        "snmp_enabled": "true" if getattr(device, "snmp", False) else "false",
        "snmp_description": _text(getattr(device, "description", "")),
        "snmp_uptime": _text(getattr(device, "uptime", "")),
        "snmp_contact": _text(getattr(device, "contact", "")),
        "snmp_location": _text(getattr(device, "location", "")),
        "model": _text(getattr(device, "model", "")),
        "firmware": _text(getattr(device, "firmware", "")),
        "serial": _text(getattr(device, "serial", "")),
    }


def device_export(argv=None):
    """Run a live scan and export discovered devices to CSV."""
    parser = argparse.ArgumentParser(
        prog="nm device export",
        description=(
            "Scan the network and export discovered device observations "
            "to a versioned CSV file."
        ),
    )
    parser.add_argument(
        "--output",
        "-o",
        help=(
            "Output CSV path. Defaults to "
            "netmonitor-inventory-<UTC timestamp>.csv in the current directory."
        ),
    )
    args = parser.parse_args(argv)

    exported_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    default_name = (
        "netmonitor-inventory-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + ".csv"
    )
    output_path = Path(args.output).expanduser() if args.output else Path(default_name)

    try:
        # Import inside the function because cli.py adds the engine directory
        # to sys.path during startup.
        from inventory import scanner

        print("Running live network discovery. This may take some time...")
        devices = scanner.scan()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        export_id = str(uuid.uuid4())

        # utf-8-sig helps Excel on Windows recognize UTF-8; CSV remains UTF-8.
        with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=CSV_FIELDS,
                extrasaction="ignore",
                lineterminator="\n",
            )
            writer.writeheader()
            for device in devices:
                writer.writerow(_device_row(device, export_id, exported_at))

        print()
        print(f"Exported {len(devices)} discovered device(s).")
        print(f"Schema version : {SCHEMA_VERSION}")
        print(f"Export ID      : {export_id}")
        print(f"Output file    : {output_path.resolve()}")
        print()
        print("Note: this is a live discovery export, not the configured monitoring list.")
        print("No passwords, private keys, or monitoring configuration are exported.")

    except KeyboardInterrupt:
        print("\nExport cancelled; no further action taken.")
        return 130
    except Exception as exc:
        print(f"ERROR: Inventory export failed: {exc}", file=sys.stderr)
        return 1

    return 0
