#!/usr/bin/env python3

import os

VERSION = "0.5.0-dev1"
CODENAME = "Console"


def clear():
    os.system("clear")


def banner():

    clear()

    print(r"""
 ███████╗ ██████╗ ██████╗ ██╗   ██╗████████╗
 ██╔════╝██╔════╝██╔═══██╗██║   ██║╚══██╔══╝
 ███████╗██║     ██║   ██║██║   ██║   ██║
 ╚════██║██║     ██║   ██║██║   ██║   ██║
 ███████║╚██████╗╚██████╔╝╚██████╔╝   ██║
 ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝
""")

    print(f" Scout Network Monitor {VERSION}")
    print(f" Codename: {CODENAME}")
    print("=" * 42)
    print()

def title(text):

    clear()

    banner()

    print(text)
    print("-" * len(text))
    print()
