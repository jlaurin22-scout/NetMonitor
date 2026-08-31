#!/usr/bin/env python3

from flask import Blueprint, render_template

from engine import analyzer
from engine import config


analysis = Blueprint(
    "analysis",
    __name__,
    url_prefix="/analysis"
)


@analysis.route("/")
def index():

    customer = config.load_customer()

    report = analyzer.analyze()

    return render_template(
        "analysis.html",
        customer=customer.get(
            "customer",
            "Unknown"
        ),
        address=customer.get(
            "address",
            ""
        ),
        report=report,
    )