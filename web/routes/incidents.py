#!/usr/bin/env python3

from flask import Blueprint, render_template

from engine import config
from engine import database


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