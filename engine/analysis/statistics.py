#!/usr/bin/env python3

MAJOR_OUTAGE_THRESHOLD = 10


def build_statistics(report, incidents, devices):

    for incident in incidents:

        objects = sorted(
            devices.get(obj, obj)
            for obj in incident["objects"]
        )

        if len(objects) == 1:

            report["single_device"] += 1
            report["device_counter"][objects[0]] += 1

        elif len(objects) >= MAJOR_OUTAGE_THRESHOLD:

            report["major_outages"] += 1
            report["major_events"].append(objects)

        else:

            report["multi_device"] += 1

            for obj in objects:

                report["device_counter"][obj] += 1

            report["pair_counter"][tuple(objects)] += 1