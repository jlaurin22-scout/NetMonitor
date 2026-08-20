#!/usr/bin/env python3

from datetime import datetime

from engine.network import (
    ping,
    dns_lookup
)

from engine.state import update
from engine.classifier import classify
from engine.database import add_event, update_status
from engine.constants import STATE_UP, STATE_DOWN


def event(job, state, duration):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if state == STATE_DOWN:

        message = "Unreachable"

    elif duration is None:

        message = "Available"

    else:

        if duration < 60:

            text = f"{duration}s"

        elif duration < 3600:

            minutes, seconds = divmod(
                duration,
                60
            )

            if seconds:

                text = f"{minutes}m {seconds}s"

            else:

                text = f"{minutes}m"

        else:

            hours, remainder = divmod(
                duration,
                3600
            )

            minutes = remainder // 60

            if minutes:

                text = f"{hours}h {minutes}m"

            else:

                text = f"{hours}h"

        message = f"Recovered ({text})"

    add_event(
        timestamp,
        job["name"],
        job["type"],
        state,
        message
    )

    print(
        f"{timestamp}  EVENT    {message}"
    )


def run(job):

    timestamp = datetime.now().strftime(
        "%H:%M:%S"
    )

    network = job.get("network")

    if job["type"] == "gateway":

        state = (
            STATE_UP
            if ping(
                job["ip"],
                network
            )
            else STATE_DOWN
        )

    elif job["type"] == "internet":

        state = STATE_DOWN

        for target in job["targets"]:

            if ping(
                target,
                network
            ):

                state = STATE_UP
                break

    elif job["type"] == "dns":

        state = (
            STATE_UP
            if dns_lookup(
                job["server"],
                job["lookup"],
                network
            )
            else STATE_DOWN
        )

    elif job["type"] == "device":

        state = (
            STATE_UP
            if ping(
                job["ip"],
                network
            )
            else STATE_DOWN
        )

    else:

        return

    has_changed, duration = update(
        job,
        state
    )

    update_status(
        job["name"],
        job["type"],
        state
    )

    print(
        f"{timestamp}  CHECK    "
        f"{job['name']:<20} {state}"
    )

    if has_changed:

        event(
            job,
            state,
            duration
        )