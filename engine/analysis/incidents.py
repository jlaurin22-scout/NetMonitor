#!/usr/bin/env python3

from datetime import datetime, timedelta


MERGE_WINDOW = timedelta(seconds=30)


def network_from_name(name):

    if name.startswith("LAN "):

        return "LAN"

    if name.startswith("WAN "):

        return "WAN"

    if name == "OPNSense":

        return "LAN"

    if name == "DIGIBox":

        return "WAN"

    return None


def build_incidents(rows):

    raw = []

    active = set()
    current = None

    for row in reversed(rows):

        name = row["job_name"]
        job_type = row["job_type"]

        if row["state"] == "DOWN":

            if not active:

                current = {
                    "start": row["timestamp"],
                    "end": None,
                    "objects": set(),
                    "object_types": {},
                    "networks": set()
                }

            active.add(name)

            if current:

                current["objects"].add(name)

                current["object_types"][
                    name
                ] = job_type

                network = network_from_name(name)

                if network:

                    current["networks"].add(network)

        elif row["state"] == "UP":

            active.discard(name)

            if current:

                current["objects"].add(name)

                current["object_types"][
                    name
                ] = job_type

                network = network_from_name(name)

                if network:

                    current["networks"].add(network)

            if current and not active:

                current["end"] = row["timestamp"]

                start = datetime.strptime(
                    current["start"],
                    "%Y-%m-%d %H:%M:%S"
                )

                end = datetime.strptime(
                    current["end"],
                    "%Y-%m-%d %H:%M:%S"
                )

                current["duration"] = int(
                    (end - start).total_seconds()
                )

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

            previous["duration"] += incident["duration"]

            previous["objects"].update(
                incident["objects"]
            )

            previous["object_types"].update(
                incident["object_types"]
            )

            previous["networks"].update(
                incident["networks"]
            )

        else:

            incidents.append(incident)

    return incidents