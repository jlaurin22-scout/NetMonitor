#!/usr/bin/env python3

import sqlite3

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
