#!/usr/bin/env python3

from datetime import datetime, timedelta
from html import escape


def _row_value(row, key, default=None):
    """Read a value from dict-like rows and sqlite3.Row objects."""
    try:
        return row[key]
    except (KeyError, IndexError, TypeError):
        return default


def _timestamp(value):
    if isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d %H:%M:%S"
        )
    except (TypeError, ValueError):
        return None


def _network_lanes(networks):
    lanes = []

    for index, network in enumerate(networks or []):
        network_id = network.get("id", index + 1)
        network_name = network.get("name") or f"Network {network_id}"
        gateway_name = network.get("gateway_name") or "Gateway"

        lanes.extend(
            [
                (
                    network_id,
                    "gateway",
                    f"{network_name} — {gateway_name}"
                ),
                (
                    network_id,
                    "internet",
                    f"{network_name} Internet"
                ),
                (
                    network_id,
                    "dns",
                    f"{network_name} DNS"
                ),
            ]
        )

    return lanes


def _match_lane(job_type, job_name, networks):
    job_type = str(job_type or "").lower()
    name = str(job_name or "")

    for network in networks or []:
        network_id = network.get("id")
        network_name = network.get("name") or f"Network {network_id}"
        gateway_name = network.get("gateway_name") or "Gateway"

        if job_type == "gateway" and name == gateway_name:
            return (
                network_id,
                "gateway",
                f"{network_name} — {gateway_name}"
            )

        if (
            job_type == "internet"
            and name == f"{network_name} Internet"
        ):
            return (
                network_id,
                "internet",
                f"{network_name} Internet"
            )

        if (
            job_type == "dns"
            and name == f"{network_name} DNS"
        ):
            return (
                network_id,
                "dns",
                f"{network_name} DNS"
            )

    return None


def build_core_network_graph(
    events,
    networks=None,
    now=None
):
    """
    Render configured core-network event history as an inline SVG.

    Labels and lanes come from the site's configured networks.
    Event markers come from the site's stored database events.
    """

    networks = networks or []
    now = now or datetime.now()
    start = now - timedelta(days=7)

    configured_lanes = _network_lanes(networks)
    lane_keys = {
        (network_id, job_type): index
        for index, (network_id, job_type, _label) in enumerate(
            configured_lanes
        )
    }

    points = []

    for event in events:
        job_type = str(
            _row_value(event, "job_type") or ""
        ).lower()

        if job_type not in {
            "gateway",
            "internet",
            "dns"
        }:
            continue

        ts = _timestamp(
            _row_value(event, "timestamp")
        )

        if (
            ts is None
            or ts < start
            or ts > now
        ):
            continue

        state = str(
            _row_value(event, "state") or ""
        ).upper()

        if state not in {
            "DOWN",
            "UP"
        }:
            continue

        matched = _match_lane(
            job_type,
            _row_value(event, "job_name"),
            networks
        )

        if matched is None:
            continue

        network_id, lane_type, label = matched

        lane_index = lane_keys.get(
            (network_id, lane_type)
        )

        if lane_index is None:
            continue

        points.append(
            (
                ts,
                lane_index,
                state,
                label
            )
        )

    points.sort(
        key=lambda item: item[0]
    )

    # Only show lanes that actually have events in this site's
    # database. Do not create empty lanes merely because a network
    # has a possible gateway/internet/dns configuration.
    active_lane_keys = {
        (network_id, lane_type)
        for _ts, lane_index, _state, _label in points
        for network_id, lane_type, _lane_label in [configured_lanes[lane_index]]
    }

    lanes = [
        lane
        for lane in configured_lanes
        if (lane[0], lane[1]) in active_lane_keys
    ]

    lane_index_map = {
        (network_id, lane_type): index
        for index, (network_id, lane_type, _label) in enumerate(lanes)
    }

    remapped_points = []

    for ts, old_lane_index, state, label in points:
        network_id, lane_type, _old_label = configured_lanes[old_lane_index]
        new_lane_index = lane_index_map.get(
            (network_id, lane_type)
        )

        if new_lane_index is not None:
            remapped_points.append(
                (
                    ts,
                    new_lane_index,
                    state,
                    label
                )
            )

    points = remapped_points

    width = 1200
    height = max(
        520,
        120 + len(lanes) * 85
    )

    # Reserve a dedicated label column outside the plotting area.
    left = 300
    right = 25
    top = 70
    bottom = 65

    plot_w = width - left - right
    plot_h = height - top - bottom

    total_seconds = max(
        1,
        (now - start).total_seconds()
    )

    def xpos(ts):
        return (
            left
            + (
                (ts - start).total_seconds()
                / total_seconds
            )
            * plot_w
        )

    if lanes:
        lane_spacing = (
            plot_h / max(1, len(lanes) - 1)
            if len(lanes) > 1
            else 0
        )
        lane_y = {
            index: (
                top + lane_spacing * index
                if len(lanes) > 1
                else top + plot_h / 2
            )
            for index in range(len(lanes))
        }
    else:
        lane_y = {}

    site_label = (
        "Configured core network"
        if lanes
        else "No configured core-network monitors"
    )

    svg = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" '
            'role="img" aria-label="Core network events for the past seven days">'
        ),
        '<rect width="100%" height="100%" fill="white"/>',
        (
            f'<text x="{width / 2:.1f}" y="28" '
            'text-anchor="middle" '
            'font-family="Arial, sans-serif" font-size="18" fill="#222">'
            'Core network events — past 7 days</text>'
        ),
    ]

    for index, (_network_id, _job_type, label) in enumerate(lanes):
        yy = lane_y[index]

        svg.append(
            (
                f'<line x1="{left}" y1="{yy:.1f}" '
                f'x2="{width - right}" y2="{yy:.1f}" '
                'stroke="#dddddd" stroke-width="1"/>'
            )
        )

        svg.append(
            (
                f'<text x="{left - 12}" y="{yy + 5:.1f}" '
                'text-anchor="end" '
                'font-family="Arial, sans-serif" font-size="12" fill="#222">'
                f'{escape(str(label))}</text>'
            )
        )

    first_day = start.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    tick = first_day

    while tick <= now:
        xx = xpos(tick)

        svg.append(
            (
                f'<line x1="{xx:.1f}" y1="{top}" '
                f'x2="{xx:.1f}" y2="{top + plot_h:.1f}" '
                'stroke="#e6e6e6" stroke-width="1"/>'
            )
        )

        svg.append(
            (
                f'<text x="{xx:.1f}" y="{height - 34}" '
                'text-anchor="middle" '
                'font-family="Arial, sans-serif" font-size="11" fill="#444">'
                f'{tick.strftime("%d %b")}</text>'
            )
        )

        tick += timedelta(days=1)

    for ts, lane_index, state, label in points:
        xx = xpos(ts)
        yy = lane_y[lane_index]

        color = (
            "#d9534f"
            if state == "DOWN"
            else "#f0ad4e"
        )

        size = 5

        if state == "UP":
            pts = (
                f"{xx:.1f},{yy - size:.1f} "
                f"{xx - size:.1f},{yy + size:.1f} "
                f"{xx + size:.1f},{yy + size:.1f}"
            )
        else:
            pts = (
                f"{xx:.1f},{yy + size:.1f} "
                f"{xx - size:.1f},{yy - size:.1f} "
                f"{xx + size:.1f},{yy - size:.1f}"
            )

        title = (
            f"{ts.strftime('%d %b %Y %H:%M:%S')} "
            f"— {label} {state}"
        )

        svg.append(
            (
                f'<g><title>{escape(title)}</title>'
                f'<polygon points="{pts}" fill="{color}"/></g>'
            )
        )

    # Legend sits in the header area above the plotting area,
    # completely clear of the event markers.
    lx = width - right - 125
    ly = 30

    svg.append(
        (
            f'<rect x="{lx - 10}" y="{ly - 14}" '
            'width="145" height="50" rx="4" '
            'fill="white" stroke="#d5d5d5"/>'
        )
    )

    svg.append(
        (
            f'<polygon points="{lx},{ly + 15} '
            f'{lx - 5},{ly + 5} {lx + 5},{ly + 5}" '
            'fill="#d9534f"/>'
        )
    )

    svg.append(
        (
            f'<text x="{lx + 15}" y="{ly + 12}" '
            'font-family="Arial, sans-serif" '
            'font-size="11" fill="#333">DOWN</text>'
        )
    )

    svg.append(
        (
            f'<polygon points="{lx},{ly + 25} '
            f'{lx - 5},{ly + 35} {lx + 5},{ly + 35}" '
            'fill="#f0ad4e"/>'
        )
    )

    svg.append(
        (
            f'<text x="{lx + 15}" y="{ly + 33}" '
            'font-family="Arial, sans-serif" '
            'font-size="11" fill="#333">UP</text>'
        )
    )

    svg.append(
        (
            f'<text x="{width / 2:.1f}" y="{height - 8}" '
            'text-anchor="middle" '
            'font-family="Arial, sans-serif" font-size="11" fill="#555">'
            'Date and exact time</text>'
        )
    )

    svg.append('</svg>')

    return ''.join(svg)
