#!/usr/bin/env python3

import os
from engine.constants import VERSION, BUILD, CODENAME

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

    print(
        f"{BOLD}{WHITE} Scout Network Monitor "
        f"{GREEN}{VERSION}-{BUILD}{RESET}"
    )
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

def state(state):

    if state == "UP":
        return f"{GREEN}● UP{RESET}"

    if state == "DOWN":
        return f"{RED}● DOWN{RESET}"

    return state
