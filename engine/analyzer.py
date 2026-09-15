from engine.database import get_incidents

from engine.config import get_devices, load_customer

from engine.analysis.health import calculate_health
from engine.analysis.summary import build_summary
from engine.analysis.statistics import build_statistics
from engine.analysis.findings import build_findings
from engine.analysis.report import create_report
from engine.analysis.reliability import calculate_reliability
from engine.analysis.ranking import rank_findings
from engine.analysis.chart import build_core_network_graph

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

    report["incidents"] = incidents

    build_statistics(
        report,
        incidents,
        devices
    )

    calculate_health(report)

    build_findings(report)

    rank_findings(report)

    calculate_reliability(report)

    build_summary(report)

    customer = load_customer()

    report["core_network_graph"] = build_core_network_graph(
        incidents
    )

    return report
