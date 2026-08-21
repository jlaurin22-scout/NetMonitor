#!/usr/bin/env python3

import ui
from engine import database


def clear_events():

    print("Clear Event History")
    print("===================")
    print()

    print("This will permanently delete:")
    print("  • All recorded events")
    print("  • All derived incidents")
    print()

    print("The following will NOT be affected:")
    print("  ✓ Customer configuration")
    print("  ✓ Site configuration")
    print("  ✓ Device configuration")
    print("  ✓ Current monitoring")
    print()

    answer = input("Type YES to continue: ")

    if answer != "YES":

        print()
        print("Operation cancelled.")
        return

    database.clear_history()

    print()
    print("Event history successfully cleared.")
    print("Scout will now begin recording a new history.")


def events(limit=50):

    print("Recent Events")
    print("-------------")
    print()

    rows = database.get_recent_events(limit)

    if not rows:

        ui.info("No events recorded.")
        print()
        return

    print(
        f"{'TIME':<20}"
        f"{'STATE':<6}"
        f"{'NAME':<24}"
        f"MESSAGE"
    )

    print("-" * 80)

    for row in rows:

        name = row["job_name"]

        if ":" in name:

            name = name.split(":", 1)[1]

        print(
            f"{row['timestamp']:<20}"
            f"{row['state']:<6}"
            f"{name:<24}"
            f"{row['message']}"
        )

    print()


def format_duration(seconds):

    seconds = int(seconds)

    minutes, seconds = divmod(
        seconds,
        60
    )

    hours, minutes = divmod(
        minutes,
        60
    )

    if hours:

        return f"{hours}h {minutes}m {seconds}s"

    if minutes:

        return f"{minutes}m {seconds}s"

    return f"{seconds}s"


def incidents():

    incidents = database.get_incidents()

    if not incidents:

        print("No incidents found.\n")
        return

    for i, incident in enumerate(
        reversed(incidents),
        1
    ):

        print(f"Incident {i}")
        print("-" * 60)

        print(
            f"Started : {incident['start']}"
        )

        print(
            f"Ended   : {incident['end']}"
        )

        print(
            f"Duration: "
            f"{format_duration(incident['duration'])}"
        )

        print()

        primary = incident.get(
            "primary"
        )

        if primary:

            print("Diagnosis")
            print("---------")

            print(
                f"Primary : "
                f"{primary['object']}"
            )

            print(
                f"Type    : "
                f"{primary['job_type']}"
            )

            print(
                f"Network : "
                f"{primary['network'] or 'Unknown'}"
            )

            print(
                f"Time    : "
                f"{primary['timestamp']}"
            )

            print(
                f"Confidence: "
                f"{primary['confidence']}"
            )

            print()

            print(
                incident.get(
                    "diagnosis",
                    "No diagnosis available."
                )
            )

            print()

        dependents = incident.get(
            "dependents",
            []
        )

        if dependents:

            print("Dependent Impact")
            print("----------------")

            for item in dependents:

                print(
                    f"  {item['object']:<24}"
                    f"+{item['delay']}s"
                )

            print()

        flapping = incident.get(
            "flapping",
            []
        )

        if flapping:

            print("Flapping")
            print("--------")

            for item in flapping:

                print(
                    f"  {item['object']:<24}"
                    f"{item['episodes']} episodes"
                )

            print()

        secondary = incident.get(
            "secondary",
            []
        )

        if secondary:

            print("Secondary Failures")
            print("------------------")

            for item in secondary:

                print(
                    f"  {item['object']:<24}"
                    f"+{item['delay']}s"
                )

            print()

        episodes = incident.get(
            "episodes",
            []
        )

        if episodes:

            print("Failure Episodes")
            print("----------------")

            for episode in sorted(
                episodes,
                key=lambda item: (
                    item["start"],
                    item["object"]
                )
            ):

                print(
                    f"  {episode['object']:<24}"
                    f"{episode['start'][11:19]} - "
                    f"{episode['end'][11:19]}  "
                    f"{format_duration(episode['duration'])}"
                )

            print()

        print("Affected:")

        for obj in sorted(
            incident["objects"]
        ):

            print(f"  {obj}")

        print()