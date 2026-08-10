#!/usr/bin/env python3

import ui
from engine import database

def clear_events():

    banner()

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

    banner()

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
    
def incidents():

    from datetime import datetime

    banner()

    incidents = database.get_incidents()

    if not incidents:
        print("No incidents found.\n")
        return

    for i, incident in enumerate(reversed(incidents), 1):

        start = datetime.strptime(
            incident["start"], "%Y-%m-%d %H:%M:%S"
        )
        end = datetime.strptime(
            incident["end"], "%Y-%m-%d %H:%M:%S"
        )

        duration = end - start

        print(f"Incident {i}")
        print("-" * 60)
        print(f"Started : {incident['start']}")
        print(f"Ended   : {incident['end']}")
        print(f"Duration: {duration}")
        print("Affected:")

        for obj in sorted(incident["objects"]):
            print(f"  {obj}")

        print()

