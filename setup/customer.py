#!/usr/bin/env python3


def run():

    print("Customer Setup")
    print("--------------")

    customer = input(
        "Customer Name : "
    ).strip()

    address = input(
        "Address       : "
    ).strip()

    print()

    return {
        "customer": customer,
        "address": address
    }