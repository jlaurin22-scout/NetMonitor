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


def event(job, state, duration, details=None):

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

    if details:

        message += f" ({details})"

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
    
    details = None

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

        if state == STATE_DOWN:
            details = "DNS server unreachable"

        #
        # Step 2 - Verify DNS resolution
        #
        if state == STATE_UP:

            success, details = dns_lookup(
                job["server"],
                job["lookup"]
            )

            state = STATE_UP if success else STATE_DOWN

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

    if details:
        print(f"{timestamp}  CHECK    {job['name']:<20} {state} ({details})")
    else:
        print(f"{timestamp}  CHECK    {job['name']:<20} {state}")

    if has_changed:

        event(job, state, duration, details)
