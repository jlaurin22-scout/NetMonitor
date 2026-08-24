#!/usr/bin/env python3

MAJOR_OUTAGE_THRESHOLD = 10

BRIEF_INTERRUPTION_SECONDS = 30
MAJOR_SERVICE_OUTAGE_SECONDS = 300

INFRASTRUCTURE_TYPES = {
    "gateway",
    "internet",
    "dns"
}

CRITICAL_SERVICE_TYPES = {
    "gateway",
    "internet",
    "dns"
}


def classify_service_outage(
    duration,
    object_types
):

    critical_services = [
        object_type
        for object_type in object_types.values()
        if object_type in CRITICAL_SERVICE_TYPES
    ]

    if len(set(critical_services)) > 1:

        return "MAJOR OUTAGE"

    if duration > MAJOR_SERVICE_OUTAGE_SECONDS:

        return "MAJOR SERVICE OUTAGE"

    if duration >= BRIEF_INTERRUPTION_SECONDS:

        return "SERVICE OUTAGE"

    return "BRIEF INTERRUPTION"


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
        # Count actual device outages independently
        # of infrastructure incidents.
        #
        for device in monitored_devices:

            report["device_counter"][
                devices.get(device, device)
            ] += 1

        #
        # If exactly one monitored device was affected,
        # record a single-device incident even when it
        # occurred during an infrastructure incident.
        #
        if len(monitored_devices) == 1:

            report["single_device"] += 1

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

            report["pair_counter"][
                tuple(names)
            ] += 1

        #
        # Infrastructure failure.
        #
        if infrastructure:

            service_objects = {
                devices.get(
                    obj,
                    obj
                ): object_types.get(
                    obj
                )
                for obj in infrastructure
            }

            duration = incident.get(
                "duration",
                0
            )

            severity = classify_service_outage(
                duration,
                service_objects
            )

            report["service_outages"].append(
                {
                    "start": incident.get(
                        "start"
                    ),
                    "end": incident.get(
                        "end"
                    ),
                    "duration": duration,
                    "severity": severity,
                    "networks": sorted(
                        networks
                    ),
                    "objects": sorted(
                        service_objects
                    ),
                    "object_types": service_objects
                }
            )

            #
            # A failure affecting multiple networks
            # remains a major infrastructure event.
            #
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
                        "objects": sorted(
                            infrastructure
                        )
                    }
                )

            continue