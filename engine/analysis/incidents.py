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

    networks = networks or []
    devices = devices or []


    #
    # Device jobs use the network ID as a prefix:
    #
    #     2:NAS-STIEL
    #     3:Fritz!Box PBX
    #
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

            #
            # Prefer the configured device network assignment.
            #
            for device in devices:

                if device.get("name") == device_name:

                    network_id = device.get(
                        "network_id",
                        network_id
                    )

                    break

            #
            # Resolve the network ID through the configured
            # customer networks.
            #
            for network in networks:

                if network.get("id") == network_id:

                    return network.get("name")

        name = device_name

    #
    # Resolve gateway jobs from the configured gateway_name.
    #
    # This replaces the old hard-coded:
    #
    #     OPNSense -> LAN
    #     DIGIBox  -> WAN
    #
    # behavior.
    #
    for network in networks:

        gateway_name = network.get(
            "gateway_name"
        )

        if (
            gateway_name
            and
            name == gateway_name
        ):

            return network.get("name")

    #
    # Internet and DNS jobs are generated using the
    # configured network name:
    #
    #     LAN Internet
    #     LAN DNS
    #     WAN Internet
    #     WAN DNS
    #     Primary Internet
    #     Primary DNS
    #
    for network in networks:

        network_name = network.get(
            "name"
        )

        if not network_name:

            continue

        if name in (
            f"{network_name} Internet",
            f"{network_name} DNS"
        ):

            return network_name

    #
    # If the job name exactly matches a configured
    # network name, resolve it directly.
    #
    for network in networks:

        if name == network.get("name"):

            return network.get("name")

    #
    # Preserve the old generic LAN/WAN naming behavior
    # only when those networks are actually configured.
    #
    for network in networks:

        network_name = network.get(
            "name"
        )

        if (
            network_name
            and
            name.startswith(
                f"{network_name} "
            )
        ):

            return network_name

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

    #
    # Multiple incidents may now remain open at the
    # same time. Each incident has its own active
    # device/job episodes.
    #
    open_incidents = []

    #
    # Maps job name to:
    #
    #     (incident, episode)
    #
    active = {}

    for row in reversed(rows):

        name = row["job_name"]
        job_type = row["job_type"]

        display_name = display_name_from_name(
            name,
            devices
        )

        timestamp = row["timestamp"]

        if row["state"] == "DOWN":

            #
            # Ignore duplicate DOWN events while this
            # particular job is already active.
            #
            if name in active:

                incident, episode = active[name]

                incident["objects"].add(
                    display_name
                )

                incident["object_types"][
                    display_name
                ] = job_type

                network = network_from_name(
                    name,
                    networks,
                    devices
                )

                if network:

                    incident["networks"].add(
                        network
                    )

                continue

            timestamp_dt = parse_timestamp(
                timestamp
            )

            candidate = None

            #
            # Find the most recently started open
            # incident that is still inside the
            # existing merge window.
            #
            for incident in reversed(
                open_incidents
            ):

                incident_start = parse_timestamp(
                    incident["start"]
                )

                delay = (
                    timestamp_dt
                    -
                    incident_start
                )

                if (
                    delay.total_seconds()
                    < 0
                ):

                    continue

                if (
                    delay
                    <= MERGE_WINDOW
                ):

                    candidate = incident
                    break

            #
            # No suitable open incident:
            # create a completely new one.
            #
            if candidate is None:

                candidate = {
                    "start": timestamp,
                    "end": None,
                    "objects": set(),
                    "object_types": {},
                    "networks": set(),
                    "episodes": []
                }

                open_incidents.append(
                    candidate
                )

            episode = create_episode(
                row,
                networks,
                devices
            )

            active[name] = (
                candidate,
                episode
            )

            candidate["episodes"].append(
                episode
            )

            candidate["objects"].add(
                display_name
            )

            candidate["object_types"][
                display_name
            ] = job_type

            network = network_from_name(
                name,
                networks,
                devices
            )

            if network:

                candidate["networks"].add(
                    network
                )

        elif row["state"] == "UP":

            #
            # A recovery belongs to the incident
            # that contains the corresponding active
            # episode.
            #
            if name not in active:

                continue

            incident, episode = active.pop(
                name
            )

            finalize_episode(
                episode,
                timestamp
            )

            incident["objects"].add(
                display_name
            )

            incident["object_types"][
                display_name
            ] = job_type

            network = network_from_name(
                name,
                networks,
                devices
            )

            if network:

                incident["networks"].add(
                    network
                )

            #
            # Determine whether this incident still
            # contains any active episodes.
            #
            still_active = any(
                item[0] is incident
                for item in active.values()
            )

            if not still_active:

                incident["end"] = timestamp

                start = parse_timestamp(
                    incident["start"]
                )

                end = parse_timestamp(
                    incident["end"]
                )

                incident["duration"] = int(
                    (
                        end - start
                    ).total_seconds()
                )

                analyze_incident(
                    incident
                )

                if incident in open_incidents:

                    open_incidents.remove(
                        incident
                    )

                raw.append(
                    incident
                )

    #
    # Any incident that is still open remains ACTIVE.
    #
    for incident in open_incidents:

        if incident in raw:

            continue

        if incident.get("episodes"):

            active_episodes = [
                episode
                for episode in incident["episodes"]
                if episode.get("end") is None
            ]

            if active_episodes:

                incident["end"] = (
                    active_episodes[-1]["start"]
                )

            else:

                incident["end"] = (
                    incident["episodes"][-1]["end"]
                )

            start = parse_timestamp(
                incident["start"]
            )

            end = parse_timestamp(
                incident["end"]
            )

            incident["duration"] = int(
                (
                    end - start
                ).total_seconds()
            )

            analyze_incident(
                incident
            )

            raw.append(
                incident
            )

    if not raw:

        return []

    #
    # Multiple incidents can finish in a different
    # order than they started. Sort them before the
    # existing merge pass.
    #
    raw.sort(
        key=lambda incident: incident["start"]
    )

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
