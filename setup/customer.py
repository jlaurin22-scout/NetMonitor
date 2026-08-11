#!/usr/bin/env python3

def run():

    print("Customer Setup")
    print("--------------")

    customer = input(
        "Customer Name : "
    ).strip()

    site = input(
        "Site Name     : "
    ).strip()

    print()

    return {
        "customer": customer,
        "site": site
    }
