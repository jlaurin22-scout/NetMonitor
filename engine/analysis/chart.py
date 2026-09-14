#!/usr/bin/env python3

from datetime import datetime, timedelta


def _timestamp(value):
    if isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return None


def _label(job_type, job_name):
    job_type = str(job_type or "").lower()
    name = str(job_name or "")

    if job_type == "gateway":
        return "OPNsense"

    if job_type == "internet":
        return name if name.endswith("Internet") else "LAN Internet"

    if job_type == "dns":
        return name if name.endswith("DNS") else "LAN DNS"

    return name


def build_core_network_graph(events, now=None):
    """
    Render the core-network event history as an inline SVG.

    This is generated fresh for every Analysis request and uses the
    actual event timestamps stored by Watchdog.
    """

    now = now or datetime.now()
    start = now - timedelta(days=7)

    points = []

    for event in events:
        job_type = str(event["job_type"] or "").lower()

        if job_type not in {"gateway", "internet", "dns"}:
            continue

        ts = _timestamp(event["timestamp"])

        if ts is None or ts < start or ts > now:
            continue

        state = str(event["state"] or "").upper()

        if state not in {"DOWN", "UP"}:
            continue

        points.append((ts, job_type, state, _label(job_type, event["job_name"])))

    points.sort(key=lambda item: item[0])

    # Keep the visual structure of the graph used this morning.
    width = 1200
    height = 520
    left = 105
    right = 25
    top = 55
    bottom = 65
    plot_w = width - left - right
    plot_h = height - top - bottom

    # One lane per core service. Additional WAN variants remain on the
    # same service lane, matching the morning graph's compact presentation.
    lanes = [("gateway", "OPNsense"), ("internet", "LAN Internet"), ("dns", "LAN DNS")]
    y = {
        "gateway": top + 25,
        "internet": top + plot_h / 2,
        "dns": top + plot_h - 25,
    }

    total_seconds = max(1, (now - start).total_seconds())

    def xpos(ts):
        return left + ((ts - start).total_seconds() / total_seconds) * plot_w

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        'role="img" aria-label="Watchdog core network events for the past seven days">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2:.1f}" y="25" text-anchor="middle" '
        'font-family="Arial, sans-serif" font-size="18" fill="#222">'
        'Watchdog core network events — past 7 days</text>',
    ]

    # Horizontal service lanes.
    for key, label in lanes:
        yy = y[key]
        svg.append(
            f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" '
            'stroke="#dddddd" stroke-width="1"/>'
        )
        svg.append(
            f'<text x="{left-12}" y="{yy+5:.1f}" text-anchor="end" '
            'font-family="Arial, sans-serif" font-size="12" fill="#222">'
            f'{label}</text>'
        )

    # Vertical day guides, including the current day.
    first_day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    tick = first_day
    while tick <= now:
        xx = xpos(tick)
        svg.append(
            f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{top+plot_h:.1f}" '
            'stroke="#e6e6e6" stroke-width="1"/>'
        )
        svg.append(
            f'<text x="{xx:.1f}" y="{height-34}" text-anchor="middle" '
            'font-family="Arial, sans-serif" font-size="11" fill="#444">'
            f'{tick.strftime("%d %b")}</text>'
        )
        tick += timedelta(days=1)

    # Event markers. DOWN is a downward triangle; UP is an upward triangle.
    for ts, job_type, state, label in points:
        xx = xpos(ts)
        yy = y[job_type]
        color = "#d9534f" if state == "DOWN" else "#f0ad4e"
        size = 5

        if state == "UP":
            pts = f"{xx:.1f},{yy-size:.1f} {xx-size:.1f},{yy+size:.1f} {xx+size:.1f},{yy+size:.1f}"
        else:
            pts = f"{xx:.1f},{yy+size:.1f} {xx-size:.1f},{yy-size:.1f} {xx+size:.1f},{yy-size:.1f}"

        # Exact timestamp is available on hover.
        title = f"{ts.strftime('%d %b %Y %H:%M:%S')} — {label} {state}"
        svg.append(
            f'<g><title>{title}</title><polygon points="{pts}" fill="{color}"/></g>'
        )

    # Legend.
    lx = left + 12
    ly = top + 15
    svg.append(
        f'<rect x="{lx-10}" y="{ly-14}" width="145" height="50" rx="4" '
        'fill="white" stroke="#d5d5d5"/>'
    )
    svg.append(
        f'<polygon points="{lx},{ly+15} {lx-5},{ly+5} {lx+5},{ly+5}" fill="#d9534f"/>'
    )
    svg.append(
        f'<text x="{lx+15}" y="{ly+12}" font-family="Arial, sans-serif" '
        'font-size="11" fill="#333">DOWN</text>'
    )
    svg.append(
        f'<polygon points="{lx},{ly+25} {lx-5},{ly+35} {lx+5},{ly+35}" fill="#f0ad4e"/>'
    )
    svg.append(
        f'<text x="{lx+15}" y="{ly+33}" font-family="Arial, sans-serif" '
        'font-size="11" fill="#333">UP</text>'
    )

    svg.append(
        f'<text x="{width/2:.1f}" y="{height-8}" text-anchor="middle" '
        'font-family="Arial, sans-serif" font-size="11" fill="#555">'
        'Date and exact time</text>'
    )
    svg.append('</svg>')
    return ''.join(svg)
