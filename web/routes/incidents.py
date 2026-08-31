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


incidents = Blueprint(
    "incidents",
    __name__,
    url_prefix="/incidents"
)


@incidents.route("/")
def index():

    customer = config.load_customer()

    incident_data = database.get_incidents()

    return render_template(
        "incidents.html",
        customer=customer.get(
            "customer",
            "Unknown"
        ),
        address=customer.get(
            "address",
            ""
        ),
        incidents=incident_data,
    )

@incidents.route(
    "/delete-selected",
    methods=["POST"]
)
@admin_required
def delete_selected():

    selected = request.form.getlist(
        "incident_id"
    )

    if not selected:

        return redirect(
            url_for(
                "incidents.index",
                error="No incidents selected."
            )
        )

    try:

        removed = database.delete_incidents(
            selected
        )

        return redirect(
            url_for(
                "incidents.index",
                message=(
                    f"{removed} incident"
                    f"{'s' if removed != 1 else ''} "
                    "deleted successfully."
                )
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "incidents.index",
                error=str(e)
            )
        )


@incidents.route(
    "/clear",
    methods=["POST"]
)
@admin_required
def clear():

    try:

        database.clear_incidents()

        return redirect(
            url_for(
                "incidents.index",
                message="All incidents cleared successfully."
            )
        )

    except Exception as e:

        return redirect(
            url_for(
                "incidents.index",
                error=str(e)
            )
        )
