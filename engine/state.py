#!/usr/bin/env python3

import time

STATE = {}


def update(job, new_state):

    now = time.time()

    name = job["name"]

    if name not in STATE:

        STATE[name] = {
            "state": new_state,
            "time": now,
            "type": job["type"],
            "device_type": job.get("device_type", "")
        }

        return False, None

    old_state = STATE[name]["state"]
    old_time = STATE[name]["time"]

    if old_state == new_state:
        return False, None

    duration = int(now - old_time)

    STATE[name] = {
        "state": new_state,
        "time": now,
        "type": job["type"],
        "device_type": job.get("device_type", "")
    }

    return True, duration


def current():

    return STATE
