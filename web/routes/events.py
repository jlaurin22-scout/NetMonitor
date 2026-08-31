#!/usr/bin/env python3

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for
)

from engine import config
from engine import database

from web.auth import admin_required


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
                "id": row["id"],
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

@events.route(
    "/delete-selected",
    methods=["POST"]
)
@admin_required
def delete_selected():

    selected = request.form.getlist(
        "event_id"
    )

    if not selected:

        return redirect(
            url_for(
                "events.index",
                error="No events selected."
            )
        )

    try:

        event_ids = [
            int(value)
            for value in selected
        ]

        removed = database.delete_events(
            event_ids
        )

        return redirect(
            url_for(
                "events.index",
                message=(
                    f"{removed} event"
                    f"{'s' if removed != 1 else ''} "
                    "deleted successfully."
                )
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "events.index",
                error=str(e)
            )
        )


@events.route(
    "/clear",
    methods=["POST"]
)
@admin_required
def clear():

    try:

        database.clear_events()

        return redirect(
            url_for(
                "events.index",
                message="All events cleared successfully."
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "events.index",
                error=str(e)
            )
        )
