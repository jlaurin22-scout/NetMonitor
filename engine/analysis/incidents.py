#!/usr/bin/env python3

from datetime import datetime, timedelta


MERGE_WINDOW = timedelta(seconds=30)


def build_incidents(rows):

    raw = []

    active = set()
    current = None

    for row in reversed(rows):

        name = row["job_name"]

        if row["state"] == "DOWN":

            if not active:

                current = {
                    "start": row["timestamp"],
                    "end": None,
                    "objects": set(),
                }

            active.add(name)

            if current:

                current["objects"].add(name)

        elif row["state"] == "UP":

            active.discard(name)

            if current:

                current["objects"].add(name)

            if current and not active:

                current["end"] = row["timestamp"]
                raw.append(current)
                current = None

    if not raw:

        return []

    incidents = [raw[0]]

    for incident in raw[1:]:

        previous = incidents[-1]

        previous_end = datetime.strptime(
            previous["end"],
            "%Y-%m-%d %H:%M:%S"
        )

        current_start = datetime.strptime(
            incident["start"],
            "%Y-%m-%d %H:%M:%S"
        )

        if current_start - previous_end <= MERGE_WINDOW:

            previous["end"] = incident["end"]

            previous["objects"].update(
                incident["objects"]
            )

        else:

            incidents.append(incident)

    return incidents