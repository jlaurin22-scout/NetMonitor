#!/usr/bin/env python3

import hashlib
import sqlite3

from engine.analysis.incidents import build_incidents
from engine.config import (
    get_networks,
    get_devices,
    get_device_monitoring_mode
)


DB = "/var/lib/netmonitor/netmonitor.db"


def initialize():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            job_name TEXT,
            job_type TEXT,
            state TEXT,
            message TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS current_status
        (
            job_name TEXT PRIMARY KEY,
            job_type TEXT,
            state TEXT,
            last_change TEXT
        )
    """)

    cur.execute("CREATE TABLE IF NOT EXISTS incident_dismissals "
                "(incident_id TEXT PRIMARY KEY)")

    cur.execute("CREATE TABLE IF NOT EXISTS incident_control "
                "(id INTEGER PRIMARY KEY CHECK (id = 1), "
                "cleared_before TEXT)")

    conn.commit()
    conn.close()


def add_event(timestamp, job_name, job_type, state, message):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO events
        (
            timestamp,
            job_name,
            job_type,
            state,
            message
        )
        VALUES (?,?,?,?,?)
    """,
    (
        timestamp,
        job_name,
        job_type,
        state,
        message
    ))

    cur.execute("""
        INSERT OR REPLACE INTO current_status
        (
            job_name,
            job_type,
            state,
            last_change
        )
        VALUES (?,?,?,?)
    """,
    (
        job_name,
        job_type,
        state,
        timestamp
    ))

    conn.commit()
    conn.close()


def update_status(job_name, job_type, state):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT job_name
        FROM current_status
        WHERE job_name = ?
    """,
    (
        job_name,
    ))

    existing = cur.fetchone()

    if existing:

        cur.execute("""
            UPDATE current_status
            SET
                job_type = ?,
                state = ?
            WHERE job_name = ?
        """,
        (
            job_type,
            state,
            job_name
        ))

    else:

        cur.execute("""
            INSERT INTO current_status
            (
                job_name,
                job_type,
                state,
                last_change
            )
            VALUES
            (
                ?,
                ?,
                ?,
                datetime('now','localtime')
            )
        """,
        (
            job_name,
            job_type,
            state
        ))

    conn.commit()
    conn.close()


def clear_history():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("DELETE FROM events")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='events'")

    conn.commit()
    conn.close()


def get_current_status():

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""
        SELECT
            job_name,
            job_type,
            state,
            last_change
        FROM current_status
        ORDER BY
            CASE job_type
                WHEN 'gateway' THEN 1
                WHEN 'internet' THEN 2
                WHEN 'dns' THEN 3
                WHEN 'device' THEN 4
                ELSE 5
            END,
            job_name
    """)

    rows = cur.fetchall()

    conn.close()

    return rows


def get_recent_events(limit=50):

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            timestamp,
            job_name,
            job_type,
            state,
            message
        FROM events
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()

    conn.close()

    return rows


def _incident_id(incident):

    primary = incident.get("primary") or {}

    value = "|".join(
        [
            str(incident.get("start", "")),
            str(primary.get("object", "")),
            str(primary.get("job_type", ""))
        ]
    )

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def get_incidents():

    rows = get_recent_events(1000)

    networks = get_networks()
    devices = get_devices()

    #
    # Preserve all events in the database.
    #
    # Standby devices are only excluded from
    # incident analysis. Their raw UP/DOWN events
    # remain available in the event history.
    #

    standby_devices = set()

    for device in devices:

        if (
            get_device_monitoring_mode(device)
            ==
            "standby"
        ):

            standby_devices.add(
                device.get("name")
            )

    filtered_rows = []

    for row in rows:

        if row["job_type"] != "device":

            filtered_rows.append(
                row
            )

            continue

        device_name = row["job_name"]

        if ":" in device_name:

            device_name = device_name.split(
                ":",
                1
            )[1]

        if device_name in standby_devices:

            continue

        filtered_rows.append(
            row
        )

    incidents = build_incidents(
        filtered_rows,
        networks,
        devices
    )

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT incident_id FROM incident_dismissals"
    )

    dismissed = {
        row["incident_id"]
        for row in cur.fetchall()
    }

    cur.execute(
        "SELECT cleared_before FROM incident_control "
        "WHERE id = 1"
    )

    row = cur.fetchone()

    cleared_before = row["cleared_before"] if row else None

    conn.close()

    visible = []

    for incident in incidents:

        incident["incident_id"] = _incident_id(incident)

        if incident["incident_id"] in dismissed:
            continue

        if (
            cleared_before
            and incident.get("start", "") <= cleared_before
        ):
            continue

        visible.append(incident)

    return visible


def delete_events(event_ids):

    if not event_ids:
        return 0

    event_ids = [int(event_id) for event_id in event_ids]

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    placeholders = ",".join("?" for _ in event_ids)

    cur.execute(
        f"DELETE FROM events WHERE id IN ({placeholders})",
        tuple(event_ids)
    )

    removed = cur.rowcount

    conn.commit()
    conn.close()

    return removed


def clear_events():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("DELETE FROM events")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='events'")

    conn.commit()
    conn.close()


def delete_incidents(incident_ids):

    if not incident_ids:
        return 0

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.executemany(
        "INSERT OR IGNORE INTO incident_dismissals (incident_id) VALUES (?)",
        [(incident_id,) for incident_id in incident_ids]
    )

    removed = cur.rowcount

    conn.commit()
    conn.close()

    return removed


def clear_incidents():

    from datetime import datetime

    cleared_before = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("DELETE FROM incident_dismissals")

    cur.execute(
        "INSERT OR REPLACE INTO incident_control "
        "(id, cleared_before) VALUES (1, ?)",
        (cleared_before,)
    )

    conn.commit()
    conn.close()


def remove_status(job_name):

    conn = sqlite3.connect(DB)

    cur = conn.cursor()

    cur.execute("""
        DELETE FROM current_status
        WHERE job_name = ?
    """,
    (
        job_name,
    ))

    conn.commit()
    conn.close()


def cleanup_device_status(valid_devices):

    conn = sqlite3.connect(DB)

    cur = conn.cursor()

    placeholders = ",".join("?" * len(valid_devices))

    if valid_devices:

        cur.execute(
            f"""
            DELETE FROM current_status
            WHERE job_type='device'
            AND job_name NOT IN ({placeholders})
            """,
            tuple(valid_devices)
        )

    else:

        cur.execute("""
            DELETE FROM current_status
            WHERE job_type='device'
        """)

    conn.commit()
    conn.close()


def sync_status(valid_jobs):

    conn = sqlite3.connect(DB)

    cur = conn.cursor()

    cur.execute("""
        SELECT job_name
        FROM current_status
    """)

    rows = cur.fetchall()

    valid = set(valid_jobs)

    for row in rows:

        name = row[0]

        if name not in valid:

            cur.execute("""
                DELETE FROM current_status
                WHERE job_name=?
            """,
            (
                name,
            ))

    conn.commit()
    conn.close()