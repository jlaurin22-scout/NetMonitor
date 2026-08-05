#!/usr/bin/env python3

import sqlite3
from analysis.incidents import build_incidents
from datetime import datetime

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
        INSERT OR REPLACE INTO current_status
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

def get_incidents():

    rows = get_recent_events(1000)

    return build_incidents(rows)
    
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

def sync_device_status(valid_devices):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT job_name
        FROM current_status
        WHERE job_type='device'
    """)

    rows = cur.fetchall()

    valid = set(valid_devices)

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
