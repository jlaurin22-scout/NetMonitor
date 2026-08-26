#!/usr/bin/env python3

from flask import Blueprint, render_template

from engine import config
from engine import database


events = Blueprint(
    "events",
    __name__,
    url_prefix="/events"
)


def display_name(name):

    if ":" in name:

        return name.split(
            ":",
            1
        )[1]

    return name


@events.route("/")
def index():

    customer = config.load_customer()

    event_rows = database.get_recent_events(
        100
    )

    event_data = []

    for row in event_rows:

        event_data.append(
            {
                "timestamp": row["timestamp"],
                "name": display_name(
                    row["job_name"]
                ),
                "job_type": row["job_type"],
                "state": row["state"],
                "message": row["message"],
            }
        )

    return render_template(
        "events.html",
        customer=customer.get(
            "customer",
            "Unknown"
        ),
        address=customer.get(
            "address",
            ""
        ),
        events=event_data,
    )