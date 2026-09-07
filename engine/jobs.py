#!/usr/bin/env python3

from datetime import datetime

from engine.config import get_device_expected_online

from engine.network import (
    ping,
    dns_lookup
)

from engine.state import update
from engine.database import (
    add_event,
    update_status,
    get_latest_event
)
from engine.constants import STATE_UP, STATE_DOWN
from engine.notify import send_event_notification


#
# REPORTABLE_STATE tracks the state that Watchdog has
# reported as an incident/recovery.
#
# This is deliberately separate from the physical state
# maintained by engine.state.
#
# A scheduled-offline device can therefore remain
# physically DOWN without creating an incident.
#
REPORTABLE_STATE = {}


def _initialize_reportable_state():

    if REPORTABLE_STATE:

        return

    #
    # The reportable state must come from the last
    # actual event, not current_status.
    #
    # current_status represents the physical state.
    # An event represents a state that Watchdog has
    # actually reported.
    #
    return


def _get_reportable_state(job):

    name = job["name"]

    if name in REPORTABLE_STATE:

        return REPORTABLE_STATE[name]

    latest_event = get_latest_event(
        name
    )

    if latest_event is None:

        state = STATE_UP

    else:

        state = latest_event["state"]

    REPORTABLE_STATE[name] = state

    return state


def _get_expected_online(job):

    if job["type"] != "device":

        return True

    schedule_id = job.get(
        "schedule_id"
    )

    if schedule_id is None:

        return True

    return get_device_expected_online(
        {
            "schedule_id": schedule_id
        }
    )


def _handle_device_event_state(
    job,
    physical_state,
    physical_duration,
    expected_online
):

    name = job["name"]

    reportable_state = _get_reportable_state(
        job
    )

    #
    # Physical DOWN:
    #
    # Only create a DOWN event when the device is
    # expected to be online.
    #
    if physical_state == STATE_DOWN:

        if not expected_online:

            #
            # The device is physically down, but this
            # is an expected condition.
            #
            return False, None

        #
        # The device is expected online and has not
        # already been reported DOWN.
        #
        if reportable_state == STATE_UP:

            REPORTABLE_STATE[name] = STATE_DOWN

            return True, None

        return False, None

    #
    # Physical UP:
    #
    # If Watchdog previously reported the device DOWN,
    # this is a real recovery regardless of whether the
    # device is currently inside or outside its schedule.
    #
    if physical_state == STATE_UP:

        if reportable_state == STATE_DOWN:

            REPORTABLE_STATE[name] = STATE_UP

            return True, physical_duration

        return False, None

    return False, None


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

    try:

        send_event_notification(
            job,
            state,
            duration
        )

    except Exception as e:

        print(
            f"{timestamp}  NTFY     ERROR    {e}"
        )


def run(job):

    _initialize_reportable_state()

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

    #
    # Always update the physical state first.
    #
    # This preserves the actual physical state and
    # the real physical outage duration.
    #
    physical_changed, physical_duration = update(
        job,
        state
    )

    update_status(
        job["name"],
        job["type"],
        state
    )

    #
    # Devices with availability schedules need
    # schedule-aware event handling.
    #
    if job["type"] == "device":

        expected_online = _get_expected_online(
            job
        )

        should_event, event_duration = (
            _handle_device_event_state(
                job,
                state,
                physical_duration,
                expected_online
            )
        )

        print(
            f"{timestamp}  CHECK    "
            f"{job['name']:<20} {state}"
            f"{'  EXPECTED OFFLINE' if not expected_online else ''}"
        )

        if should_event:

            event(
                job,
                state,
                event_duration
            )

        return

    print(
        f"{timestamp}  CHECK    "
        f"{job['name']:<20} {state}"
    )

    if physical_changed:

        event(
            job,
            state,
            physical_duration
        )