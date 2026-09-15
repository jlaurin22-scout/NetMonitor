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
    if value is None:
        return None
    text = str(value).strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%f",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
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
    incidents,
    now=None
):
    """
    Render ALL visible Watchdog incidents from the past seven days.

    The graph is deliberately site-agnostic: it uses the actual incident
    objects and episode timestamps produced by the incident engine. No
    network type, device name, or development-site name is assumed.
    """

    now = now or datetime.now()
    start = now - timedelta(days=7)

    rows = []

    for incident in incidents or []:
        for episode in incident.get("episodes", []) or []:
            object_name = episode.get("object")
            if not object_name:
                continue

            incident_start = _timestamp(episode.get("start"))
            if incident_start is None:
                continue

            incident_end = _timestamp(episode.get("end"))

            # Include every incident episode that overlaps the seven-day window.
            if incident_end is not None and incident_end < start:
                continue
            if incident_start > now:
                continue

            rows.append((str(object_name), incident_start, incident_end))

    # One lane per actual incident object. Preserve first-seen order.
    lane_names = []
    seen = set()

    for object_name, _incident_start, _incident_end in rows:
        if object_name not in seen:
            seen.add(object_name)
            lane_names.append(object_name)

    lane_index = {
        name: index
        for index, name in enumerate(lane_names)
    }

    points = []

    for object_name, incident_start, incident_end in rows:
        index = lane_index[object_name]

        visible_start = max(
            incident_start,
            start
        )

        points.append(
            (
                visible_start,
                index,
                "DOWN",
                object_name
            )
        )

        if incident_end is not None and incident_end <= now:
            points.append(
                (
                    incident_end,
                    index,
                    "UP",
                    object_name
                )
            )

    points.sort(
        key=lambda item: item[0]
    )

    width = 1200
    height = max(
        520,
        120 + len(lane_names) * 40
    )

    # Dedicated label column. The plotted area starts well to the right.
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

    if lane_names:
        lane_spacing = (
            plot_h / max(1, len(lane_names) - 1)
            if len(lane_names) > 1
            else 0
        )

        lane_y = {
            index: (
                top + lane_spacing * index
                if len(lane_names) > 1
                else top + plot_h / 2
            )
            for index in range(len(lane_names))
        }
    else:
        lane_y = {}

    svg = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" '
            'role="img" aria-label="Watchdog incidents for the past seven days">'
        ),
        '<rect width="100%" height="100%" fill="white"/>',
        (
            f'<text x="{width / 2:.1f}" y="25" '
            'text-anchor="middle" '
            'font-family="Arial, sans-serif" font-size="18" fill="#222">'
            'Watchdog incidents — past 7 days</text>'
        ),
    ]

    for index, label in enumerate(lane_names):
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
                f'{escape(label)}</text>'
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

    for ts, index, state, label in points:
        xx = xpos(ts)
        yy = lane_y[index]

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

    # Legend is entirely outside the plotting area.
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
