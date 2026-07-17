#!/usr/bin/env python3

import time

STATE = {}


def update(job, new_state):

    now = time.time()

    name = job["name"]

    #
    # First time we've seen this object.
    #
    if name not in STATE:

        STATE[name] = {
            "state": new_state,
            "since": now,
            "type": job["type"],
            "checks": job.get("checks", {})
        }

        return False, None

    record = STATE[name]

    #
    # No change.
    #
    if record["state"] == new_state:

        return False, None

    #
    # State changed.
    #
    duration = None

    #
    # If we're recovering from DOWN,
    # calculate the outage duration.
    #
    if record["state"] == "DOWN" and new_state == "UP":

        duration = int(now - record["since"])

    record["state"] = new_state
    record["since"] = now
    record["type"] = job["type"]
    record["checks"] = job.get("checks", {})

    return True, duration


def current():

    return STATE
