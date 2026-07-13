#!/usr/bin/env python3

from datetime import datetime

from network import ping
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

    if duration is None:
        message = f"{job['name']} is {state}"
    else:
        message = f"{job['name']} changed to {state} after {duration} seconds"

    message += f" | {classification} ({confidence}%)"

    add_event(
        timestamp,
        job["name"],
        job["type"],
        state,
        message
    )

    print(f"{timestamp}  {message}")


def run(job):

    if job["type"] == "gateway":
        state = STATE_UP if ping(job["ip"]) else STATE_DOWN

    elif job["type"] == "internet":
        state = STATE_UP if ping(job["target"]) else STATE_DOWN

    elif job["type"] == "dns":
        state = STATE_UP

    elif job["type"] == "device":
        state = STATE_UP if ping(job["ip"]) else STATE_DOWN

    else:
        return

    update_status(
        job["name"],
        job["type"],
        state
    )

    has_changed, duration = update(job, state)

    if has_changed:
        event(job, state, duration)
