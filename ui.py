#!/usr/bin/env python3

import os
RESET   = "\033[0m"

BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

BOLD    = "\033[1m"

VERSION = "0.5.0-dev1"
CODENAME = "Console"

def clear():
    os.system("clear")


def banner():

    clear()

    print(f"""{BOLD}{CYAN}
 ███████╗ ██████╗ ██████╗ ██╗   ██╗████████╗
 ██╔════╝██╔════╝██╔═══██╗██║   ██║╚══██╔══╝
 ███████╗██║     ██║   ██║██║   ██║   ██║
 ╚════██║██║     ██║   ██║██║   ██║   ██║
 ███████║╚██████╗╚██████╔╝╚██████╔╝   ██║
 ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝
{RESET}""")

    print(f"{BOLD}{WHITE} Scout Network Monitor {GREEN}{VERSION}{RESET}")
    print(f"{CYAN} Codename: {YELLOW}{CODENAME}{RESET}")
    print(f"{BLUE}{'=' * 42}{RESET}")
    print()

def title(text):

    clear()

    banner()

    print(text)
    print("-" * len(text))
    print()

def success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def error(text):
    print(f"{RED}✗ {text}{RESET}")

def info(text):
    print(f"{CYAN}ℹ {text}{RESET}")

def warning(text):
    print(f"{YELLOW}! {text}{RESET}")
