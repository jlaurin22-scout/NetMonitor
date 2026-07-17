#!/usr/bin/env python3

from datetime import datetime

from network import (
    ping,
    dns_server_reachable,
    dns_lookup
)

from state import update, current
from classifier import classify
from database import add_event, update_status
from constants import STATE_UP, STATE_DOWN


def event(job, state, duration):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status = current()

    result = classify(status)

    classification = result["classification"]
    confidence = result["confidence"]

    if state == STATE_DOWN:

        message = f"{job['name']} is DOWN"

    elif duration is None:

        message = f"{job['name']} is UP"

    else:

        message = (
            f"{job['name']} recovered "
            f"after {duration} seconds"
        )

    message += f" | {classification} ({confidence}%)"

    add_event(
        timestamp,
        job["name"],
        job["type"],
        state,
        message
    )

    print(f"{timestamp}  EVENT    {message}")


def run(job):

    timestamp = datetime.now().strftime("%H:%M:%S")

    if job["type"] == "gateway":

        state = STATE_UP if ping(job["ip"]) else STATE_DOWN

    elif job["type"] == "internet":

        state = STATE_UP if ping(job["target"]) else STATE_DOWN

    elif job["type"] == "dns":

        #
        # Step 1 - Reach the configured DNS server
        #
        state = (
            STATE_UP
            if dns_server_reachable(job["server"])
            else STATE_DOWN
        )

        #
        # Step 2 - Verify DNS resolution
        #
        if state == STATE_UP:

            state = (
                STATE_UP
                if dns_lookup(job["lookup"])
                else STATE_DOWN
            )

    elif job["type"] == "device":

        state = STATE_UP if ping(job["ip"]) else STATE_DOWN

    else:

        return

    has_changed, duration = update(job, state)

    update_status(
        job["name"],
        job["type"],
        state
    )

    print(f"{timestamp}  CHECK    {job['name']:<20} {state}")

    if has_changed:

        event(job, state, duration)
