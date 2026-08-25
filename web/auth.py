#!/usr/bin/env python3

import base64
import hashlib
import hmac
import os
import secrets
import sqlite3
from functools import wraps

from flask import (
    redirect,
    request,
    session,
    url_for,
)


DATA_DIR = "/var/lib/netmonitor"
AUTH_DB = os.path.join(DATA_DIR, "web.db")


ROLE_ADMIN = "admin"
ROLE_VIEWER = "viewer"
VALID_ROLES = (ROLE_ADMIN, ROLE_VIEWER)



def _connect():

    os.makedirs(DATA_DIR, exist_ok=True)

    connection = sqlite3.connect(
        AUTH_DB
    )

    connection.row_factory = sqlite3.Row

    return connection



def initialize():

    with _connect() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        row = connection.execute(
            "SELECT value FROM meta WHERE key = 'secret_key'"
        ).fetchone()

        if row is None:

            secret_key = secrets.token_hex(32)

            connection.execute(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                ("secret_key", secret_key)
            )

        else:

            secret_key = row["value"]

    return secret_key



def has_users():

    with _connect() as connection:

        row = connection.execute(
            "SELECT COUNT(*) AS count FROM users WHERE enabled = 1"
        ).fetchone()

    return row["count"] > 0



def hash_password(password):

    if not password:

        raise ValueError(
            "Password cannot be empty."
        )

    salt = secrets.token_bytes(16)

    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=64
    )

    return (
        "scrypt$16384$8$1$"
        f"{base64.b64encode(salt).decode()}$"
        f"{base64.b64encode(derived).decode()}"
    )



def verify_password(password, stored):

    try:

        algorithm, n, r, p, salt_text, hash_text = (
            stored.split("$", 5)
        )

        if algorithm != "scrypt":

            return False

        salt = base64.b64decode(
            salt_text
        )

        expected = base64.b64decode(
            hash_text
        )

        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected)
        )

        return hmac.compare_digest(
            derived,
            expected
        )

    except (
        ValueError,
        TypeError,
        IndexError,
    ):

        return False



def create_user(username, password, role):

    username = username.strip()

    if not username:

        raise ValueError(
            "Username cannot be empty."
        )

    if role not in VALID_ROLES:

        raise ValueError(
            "Invalid user role."
        )

    password_hash = hash_password(
        password
    )

    try:

        with _connect() as connection:

            connection.execute(
                """
                INSERT INTO users (
                    username,
                    password_hash,
                    role
                )
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    password_hash,
                    role
                )
            )

    except sqlite3.IntegrityError:

        raise ValueError(
            f'Username "{username}" already exists.'
        )



def authenticate(username, password):

    with _connect() as connection:

        user = connection.execute(
            """
            SELECT id, username, password_hash, role
            FROM users
            WHERE username = ?
              AND enabled = 1
            """,
            (username.strip(),)
        ).fetchone()

    if user is None:

        return None

    if not verify_password(
        password,
        user["password_hash"]
    ):

        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
    }



def current_user():

    if "user_id" not in session:

        return None

    return {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "role": session.get("role"),
    }



def login_user(user):

    session.clear()

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]



def logout_user():

    session.clear()



def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not has_users():

            return redirect(
                url_for("auth.uninitialized")
            )

        if current_user() is None:

            next_url = request.full_path

            if next_url.endswith("?"):

                next_url = next_url[:-1]

            return redirect(
                url_for(
                    "auth.login",
                    next=next_url
                )
            )

        return function(*args, **kwargs)

    return wrapper



def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not has_users():

            return redirect(
                url_for("auth.uninitialized")
            )

        user = current_user()

        if user is None:

            next_url = request.full_path

            if next_url.endswith("?"):

                next_url = next_url[:-1]

            return redirect(
                url_for(
                    "auth.login",
                    next=next_url
                )
            )

        if user["role"] != ROLE_ADMIN:

            return (
                "Access denied.",
                403
            )

        return function(*args, **kwargs)

    return wrapper
