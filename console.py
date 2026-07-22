#!/usr/bin/env python3

import sys
import os
import subprocess

import ui
from cli import (
    status,
    device_list,
    device_add,
    device_edit,
    device_remove
)

def devices_menu():

    while True:

        ui.banner()

        print(" Devices")
        print()

        print(" 1) List Devices")
        print(" 2) Add Device")
        print(" 3) Edit Device")
        print(" 4) Remove Device")
        print(" 5) Discover Devices")
        print()
        print(" 0) Back")
        print()

        choice = input("Selection : ").strip()

        if choice == "0":
            return

        elif choice == "1":

            ui.clear()
            device_list()
            input("Press ENTER to return...")
            ui.clear()
            return

        elif choice == "2":

            ui.clear()

            if os.geteuid() == 0:

                if device_add():
                    input("Press ENTER to return...")

            else:

                subprocess.run(["nm", "device", "add"])

            ui.clear()
            return

        elif choice == "3":

            ui.clear()

            if os.geteuid() == 0:

                device_edit()
                input("Press ENTER to return...")

            else:

                subprocess.run(["nm", "device", "edit"])

            ui.clear()
            return

        elif choice == "4":

            ui.clear()

            if os.geteuid() == 0:

                device_remove()
                input("Press ENTER to return...")

            else:

                subprocess.run(["nm", "device", "remove"])

            ui.clear()
            return

        elif choice == "5":

            print()
            print("Device Discovery")
            print("----------------")
            print("Coming in Build 0.5.0-dev2")
            input("\nPress ENTER to continue...")

        else:

            print()
            print("Invalid selection.")
            input("\nPress ENTER to continue...")

def run():

    while True:

        ui.banner()

        print(" Main Menu")
        print()
        print(" 1) Dashboard")
        print(" 2) Devices")
        print(" 3) Events")
        print(" 4) Health")
        print(" 5) Service")
        print()
        print(" 0) Exit")
        print()

        choice = input("Selection : ").strip()

        if choice == "0":
            ui.clear()
            sys.exit(0)

        elif choice == "1":

            ui.clear()
            status()
            input("Press ENTER to return...")
            ui.clear()

        elif choice == "2":

            ui.clear()
            devices_menu()

        else:

            print()
            print("Not implemented yet.")
            input("\nPress ENTER to continue...")
