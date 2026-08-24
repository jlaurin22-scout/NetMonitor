#!/usr/bin/env python3

import os
import sys

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_DIR not in sys.path:

    sys.path.insert(
        0,
        PROJECT_DIR
    )

from flask import Flask, render_template_string

from engine import config
from engine import database


app = Flask(__name__)


DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Scout Network Monitor</title>

    <style>

        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #222;
        }

        header {
            background: #1f4e79;
            color: white;
            padding: 20px 30px;
        }

        header h1 {
            margin: 0;
            font-size: 24px;
        }

        header p {
            margin: 5px 0 0;
            opacity: 0.9;
        }

        main {
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .summary {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        }

        .card h2 {
            margin-top: 0;
            font-size: 16px;
            color: #555;
        }

        .value {
            font-size: 28px;
            font-weight: bold;
        }

        .up {
            color: #198754;
        }

        .down {
            color: #dc3545;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th,
        td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background: #1f4e79;
            color: white;
        }

        tr:last-child td {
            border-bottom: none;
        }

        .status {
            font-weight: bold;
        }

        .customer {
            margin-bottom: 25px;
        }

    </style>

</head>

<body>

<header>

    <h1>Scout Network Monitor</h1>

    <p>
        {{ customer }}
        {% if address %}
            — {{ address }}
        {% endif %}
    </p>

</header>

<main>

    <div class="customer">

        <div class="card">

            <h2>Monitoring Service</h2>

            <div
                class="value
                {% if service_up %}
                    up
                {% else %}
                    down
                {% endif %}"
            >

                {{ service_state }}

            </div>

        </div>

    </div>

    <div class="summary">

        <div class="card">

            <h2>Monitored Objects</h2>

            <div class="value">
                {{ total }}
            </div>

        </div>

        <div class="card">

            <h2>UP</h2>

            <div class="value up">
                {{ up_count }}
            </div>

        </div>

        <div class="card">

            <h2>DOWN</h2>

            <div class="value down">
                {{ down_count }}
            </div>

        </div>

    </div>

    <div class="card">

        <h2>Current Status</h2>

        <table>

            <thead>

                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>State</th>
                    <th>Last Change</th>
                </tr>

            </thead>

            <tbody>

                {% for row in rows %}

                <tr>

                    <td>{{ row.name }}</td>

                    <td>{{ row.job_type }}</td>

                    <td
                        class="status
                        {% if row.state == 'UP' %}
                            up
                        {% else %}
                            down
                        {% endif %}"
                    >
                        {{ row.state }}
                    </td>

                    <td>{{ row.last_change }}</td>

                </tr>

                {% endfor %}

            </tbody>

        </table>

    </div>

</main>

</body>

</html>
"""


def get_service_state():

    rows = database.get_current_status()

    if not rows:

        return "UNKNOWN", False

    return "RUNNING", True


@app.route("/")
def dashboard():

    customer_data = config.load_customer()

    rows = database.get_current_status()

    status_rows = []

    up_count = 0
    down_count = 0

    for row in rows:

        name = row["job_name"]

        if ":" in name:

            name = name.split(
                ":",
                1
            )[1]

        state = row["state"]

        if state == "UP":

            up_count += 1

        else:

            down_count += 1

        status_rows.append(
            {
                "name": name,
                "job_type": row["job_type"],
                "state": state,
                "last_change": row["last_change"],
            }
        )

    service_state, service_up = get_service_state()

    return render_template_string(
        DASHBOARD_TEMPLATE,
        customer=customer_data.get(
            "customer",
            "Unknown"
        ),
        address=customer_data.get(
            "address",
            ""
        ),
        service_state=service_state,
        service_up=service_up,
        total=len(rows),
        up_count=up_count,
        down_count=down_count,
        rows=status_rows,
    )


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False
    )