#!/usr/bin/env python3

from engine import config


def run(networks):

    print("Configure Devices")
    print("-----------------")

    while True:

        print()

        answer = input(
            "Add monitored device? (Y/N): "
        ).strip().lower()

        if not answer.startswith("y"):

            break

        print()

        print("Networks")
        print("--------")

        for network in networks:

            print(
                f"{network['id']}) {network['name']}"
            )

        print()

        while True:

            try:

                network_id = int(
                    input("Network : ").strip()
                )

                break

            except ValueError:

                print("Invalid selection.")

        name = input(
            "Device Name : "
        ).strip()

        ip = input(
            "IP Address  : "
        ).strip()

        ping = (
            input("Ping (Y/N): ")
            .strip()
            .lower()
            .startswith("y")
        )

        snmp = (
            input("SNMP (Y/N): ")
            .strip()
            .lower()
            .startswith("y")
        )

        config.add_device(
            name=name,
            ip=ip,
            ping=ping,
            snmp=snmp,
            network_id=network_id
        )

    print()
