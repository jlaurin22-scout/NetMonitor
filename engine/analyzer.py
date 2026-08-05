from database import get_incidents, get_recent_events

from config import get_devices

from analysis.health import calculate_health
from analysis.summary import build_summary
from analysis.statistics import build_statistics
from analysis.findings import build_findings
from analysis.report import create_report
from analysis.reliability import calculate_reliability

MAJOR_OUTAGE_THRESHOLD = 10

def analyze():

    devices = {}

    for device in get_devices():

        devices[device["name"]] = device["name"]
        devices[device["ip"]] = device["name"]

    incidents = get_incidents()

    report = create_report(
        incidents,
        len(get_devices())
    )
    
    build_statistics(
        report,
        incidents,
        devices
    )

    calculate_health(report)

    build_findings(report)

    calculate_reliability(report)

    build_summary(report)

    return report