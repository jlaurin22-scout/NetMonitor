#!/usr/bin/env python3

MAJOR_OUTAGE_THRESHOLD = 10

INFRASTRUCTURE_TYPES = {
    "gateway",
    "internet",
    "dns"
}


def build_statistics(report, incidents, devices):

    for incident in incidents:

        objects = sorted(
            devices.get(obj, obj)
            for obj in incident["objects"]
        )

        object_types = incident.get(
            "object_types",
            {}
        )

        infrastructure = [
            obj
            for obj in incident["objects"]
            if object_types.get(obj) in INFRASTRUCTURE_TYPES
        ]

        monitored_devices = [
            obj
            for obj in incident["objects"]
            if object_types.get(obj) == "device"
        ]

        networks = incident.get(
            "networks",
            set()
        )

        #
        # Infrastructure failure.
        #
        # A failure confined to one network is NOT
        # a site-wide major outage.
        #
        if infrastructure:

            if len(networks) > 1:

                report["major_outages"] += 1

                report["major_events"].append(
                    {
                        "networks": sorted(networks),
                        "objects": sorted(objects)
                    }
                )

            else:

                report["infrastructure_events"].append(
                    {
                        "networks": sorted(networks),
                        "objects": sorted(objects)
                    }
                )

            continue

        #
        # Only actual monitored devices remain here.
        #
        if len(monitored_devices) == 1:

            device = monitored_devices[0]

            report["single_device"] += 1

            report["device_counter"][
                devices.get(device, device)
            ] += 1

        elif len(monitored_devices) >= MAJOR_OUTAGE_THRESHOLD:

            report["major_outages"] += 1

            report["major_events"].append(
                {
                    "networks": sorted(networks),
                    "objects": sorted(
                        devices.get(
                            obj,
                            obj
                        )
                        for obj in monitored_devices
                    )
                }
            )

        elif len(monitored_devices) > 1:

            report["multi_device"] += 1

            names = sorted(
                devices.get(
                    obj,
                    obj
                )
                for obj in monitored_devices
            )

            for name in names:

                report["device_counter"][name] += 1

            report["pair_counter"][
                tuple(names)
            ] += 1