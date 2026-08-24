#!/usr/bin/env python3

from datetime import datetime, timedelta


MERGE_WINDOW = timedelta(seconds=30)
SECONDARY_FAILURE_WINDOW = timedelta(seconds=60)
DEPENDENCY_WINDOW = timedelta(seconds=10)


def parse_timestamp(value):

    return datetime.strptime(
        value,
        "%Y-%m-%d %H:%M:%S"
    )


def display_name_from_name(
    name,
    devices=None
):

    if ":" not in name:

        return name

    prefix, device_name = name.split(
        ":",
        1
    )

    try:

        network_id = int(prefix)

    except ValueError:

        return name

    if devices:

        for device in devices:

            if (
                device["name"]
                ==
                device_name
            ):

                configured_network = device.get(
                    "network_id"
                )

                if (
                    configured_network is None
                    or
                    configured_network == network_id
                ):

                    return device["name"]

    return device_name


def network_from_name(
    name,
    networks=None,
    devices=None
):

    if ":" in name:

        prefix, device_name = name.split(
            ":",
            1
        )

        try:

            network_id = int(prefix)

        except ValueError:

            network_id = None

        if network_id is not None:

            if devices:

                for device in devices:

                    if (
                        device["name"]
                        ==
                        device_name
                    ):

                        network_id = device.get(
                            "network_id",
                            network_id
                        )

                        break

            if networks:

                for network in networks:

                    if network["id"] == network_id:

                        return network["name"]

        name = device_name

    if name.startswith("LAN "):

        return "LAN"

    if name.startswith("WAN "):

        return "WAN"

    if name == "OPNSense":

        return "LAN"

    if name == "DIGIBox":

        return "WAN"

    return None


def create_episode(
    row,
    networks=None,
    devices=None
):

    return {
        "object": display_name_from_name(
            row["job_name"],
            devices
        ),
        "job_type": row["job_type"],
        "network": network_from_name(
            row["job_name"],
            networks,
            devices
        ),
        "start": row["timestamp"],
        "end": None,
        "duration": None
    }


def finalize_episode(
    episode,
    timestamp
):

    episode["end"] = timestamp

    start = parse_timestamp(
        episode["start"]
    )

    end = parse_timestamp(
        timestamp
    )

    episode["duration"] = int(
        (end - start).total_seconds()
    )

    return episode


def analyze_incident(incident):

    episodes = incident.get(
        "episodes",
        []
    )

    if not episodes:

        return

    episodes = sorted(
        episodes,
        key=lambda item: (
            item["start"],
            item["object"]
        )
    )

    first = episodes[0]

    incident["primary"] = {
        "object": first["object"],
        "job_type": first["job_type"],
        "network": first["network"],
        "timestamp": first["start"],
        "confidence": "MEDIUM"
    }

    first_time = parse_timestamp(
        first["start"]
    )

    dependents = []
    secondary = []

    for episode in episodes[1:]:

        episode_time = parse_timestamp(
            episode["start"]
        )

        delay = (
            episode_time - first_time
        )

        object_name = episode["object"]

        previous_object_episode = any(
            previous["object"] == object_name
            and
            previous["start"] < episode["start"]
            for previous in episodes
        )

        if (
            delay <= DEPENDENCY_WINDOW
            and
            not previous_object_episode
        ):

            dependents.append(
                {
                    "object": object_name,
                    "job_type": episode["job_type"],
                    "network": episode["network"],
                    "timestamp": episode["start"],
                    "delay": int(
                        delay.total_seconds()
                    )
                }
            )

        elif (
            delay > SECONDARY_FAILURE_WINDOW
            and
            not previous_object_episode
        ):

            secondary.append(
                {
                    "object": object_name,
                    "job_type": episode["job_type"],
                    "network": episode["network"],
                    "timestamp": episode["start"],
                    "delay": int(
                        delay.total_seconds()
                    )
                }
            )

    incident["dependents"] = dependents
    incident["secondary"] = secondary

    counts = {}

    for episode in episodes:

        name = episode["object"]

        counts.setdefault(
            name,
            0
        )

        counts[name] += 1

    flapping = []

    for name, count in counts.items():

        if count >= 2:

            flapping.append(
                {
                    "object": name,
                    "episodes": count
                }
            )

    incident["flapping"] = sorted(
        flapping,
        key=lambda item: item["object"]
    )

    if dependents:

        incident["primary"]["confidence"] = "HIGH"

    incident["diagnosis"] = (
        f"{first['object']} was the first monitored "
        f"component to fail."
    )

    if dependents:

        names = ", ".join(
            item["object"]
            for item in dependents
        )

        incident["diagnosis"] += (
            f" {names} failed within "
            f"{DEPENDENCY_WINDOW.total_seconds():.0f} "
            f"seconds and may represent dependent impact."
        )

    if flapping:

        names = ", ".join(
            item["object"]
            for item in flapping
        )

        incident["diagnosis"] += (
            f" Repeated failure/recovery cycles were "
            f"detected for {names}."
        )

    if secondary:

        names = ", ".join(
            item["object"]
            for item in secondary
        )

        incident["diagnosis"] += (
            f" Later first-time failures were detected "
            f"for {names} and are classified as secondary events."
        )


def build_incidents(
    rows,
    networks=None,
    devices=None
):

    raw = []

    active = {}
    current = None

    for row in reversed(rows):

        name = row["job_name"]
        job_type = row["job_type"]

        display_name = display_name_from_name(
            name,
            devices
        )

        if row["state"] == "DOWN":

            if current is None:

                current = {
                    "start": row["timestamp"],
                    "end": None,
                    "objects": set(),
                    "object_types": {},
                    "networks": set(),
                    "episodes": []
                }

            if name not in active:

                episode = create_episode(
                    row,
                    networks,
                    devices
                )

                active[name] = episode

                current["episodes"].append(
                    episode
                )

            current["objects"].add(
                display_name
            )

            current["object_types"][
                display_name
            ] = job_type

            network = network_from_name(
                name,
                networks,
                devices
            )

            if network:

                current["networks"].add(
                    network
                )

        elif row["state"] == "UP":

            if name in active:

                episode = active.pop(
                    name
                )

                finalize_episode(
                    episode,
                    row["timestamp"]
                )

            if current:

                current["objects"].add(
                    display_name
                )

                current["object_types"][
                    display_name
                ] = job_type

                network = network_from_name(
                    name,
                    networks,
                    devices
                )

                if network:

                    current["networks"].add(
                        network
                    )

            if current and not active:

                current["end"] = row["timestamp"]

                start = parse_timestamp(
                    current["start"]
                )

                end = parse_timestamp(
                    current["end"]
                )

                current["duration"] = int(
                    (end - start).total_seconds()
                )

                analyze_incident(
                    current
                )

                raw.append(
                    current
                )

                current = None

    if current and active:

        current["end"] = current["episodes"][-1]["start"]

        start = parse_timestamp(
            current["start"]
        )

        end = parse_timestamp(
            current["end"]
        )

        current["duration"] = int(
            (end - start).total_seconds()
        )

        analyze_incident(
            current
        )

        raw.append(
            current
        )

    if not raw:

        return []

    incidents = [
        raw[0]
    ]

    for incident in raw[1:]:

        previous = incidents[-1]

        previous_end = parse_timestamp(
            previous["end"]
        )

        current_start = parse_timestamp(
            incident["start"]
        )

        if (
            current_start - previous_end
            <= MERGE_WINDOW
        ):

            previous["end"] = incident["end"]

            previous["duration"] = int(
                (
                    parse_timestamp(
                        previous["end"]
                    )
                    -
                    parse_timestamp(
                        previous["start"]
                    )
                ).total_seconds()
            )

            previous["objects"].update(
                incident["objects"]
            )

            previous["object_types"].update(
                incident["object_types"]
            )

            previous["networks"].update(
                incident["networks"]
            )

            previous["episodes"].extend(
                incident.get(
                    "episodes",
                    []
                )
            )

            analyze_incident(
                previous
            )

        else:

            incidents.append(
                incident
            )

    return incidents