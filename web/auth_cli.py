#!/usr/bin/env python3

import getpass
import sys

from web import auth


def prompt_password(label):

    while True:

        password = getpass.getpass(
            label
        )

        confirm = getpass.getpass(
            "Confirm password: "
        )

        if not password:

            print("Password cannot be empty.")
            print()
            continue

        if password != confirm:

            print("Passwords do not match.")
            print()
            continue

        return password


def create_account(role, default_username):

    while True:

        username = input(
            f"{role.title()} username [{default_username}]: "
        ).strip()

        if not username:

            username = default_username

        password = prompt_password(
            f"{role.title()} password: "
        )

        try:

            auth.create_user(
                username,
                password,
                role
            )

            print(
                f"{role.title()} account created successfully."
            )
            print()
            return

        except ValueError as error:

            print(
                f"Error: {error}"
            )
            print()


def main():

    auth.initialize()

    if auth.has_users():

        print()
        print(
            "Web authentication is already initialized."
        )
        print()
        print(
            "No changes were made."
        )
        print()
        return 0

    print()
    print("==========================================")
    print(" Scout Network Monitor Web Authentication")
    print("==========================================")
    print()
    print(
        "Create the initial Web GUI administrator"
    )
    print(
        "and viewer accounts."
    )
    print()

    create_account(
        "admin",
        "admin"
    )

    create_account(
        "viewer",
        "viewer"
    )

    print(
        "Web authentication initialized."
    )
    print()

    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )
