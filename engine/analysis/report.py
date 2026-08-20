#!/usr/bin/env python3

from collections import Counter


def create_report(incidents, devices_monitored):

    return {

        "health": "EXCELLENT",

        "devices_monitored": devices_monitored,

        "total_incidents": len(incidents),

        "single_device": 0,

        "multi_device": 0,

        "major_outages": 0,

        "device_counter": Counter(),

        "pair_counter": Counter(),

        "major_events": [],

        "infrastructure_events": [],

        "findings": [],

        "top_findings": [],

        "executive_summary": {

            "headline": "",

            "assessment": [],

            "investigation_order": []

        }

    }