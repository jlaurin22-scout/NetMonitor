from collections import Counter

from database import get_incidents, get_recent_events
from config import get_devices
from analysis.health import calculate_health
from analysis.summary import build_summary
from analysis.statistics import build_statistics
from analysis.findings import build_findings

MAJOR_OUTAGE_THRESHOLD = 10

def analyze():

    devices = {}

    for device in get_devices():

        devices[device["name"]] = device["name"]
        devices[device["ip"]] = device["name"]

    incidents = get_incidents()

    report = {
        "health": "EXCELLENT",
        "devices_monitored": len(get_devices()),
        "total_incidents": len(incidents),
        "single_device": 0,
        "multi_device": 0,
        "major_outages": 0,
        "device_counter": Counter(),
        "pair_counter": Counter(),
        "major_events": [],
        "findings": [],
        "top_findings": [],
        "executive_summary": {
            "headline": "",
            "assessment": [],
            "investigation_order": []
        }
    }

    build_statistics(
        report,
        incidents,
        devices
    )
    
    #
    # Overall Health
    #

    calculate_health(report)
    
    #
    # Findings
    #

    build_findings(report)
    
    build_summary(report)
    
    return report
