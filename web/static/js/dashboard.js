async function updateDashboard() {

    try {

        const response = await fetch(
            "/api/status",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {

            throw new Error(
                "Status request failed"
            );

        }

        const data = await response.json();

        updateHealth(data);
        updateService(data);
        updateNetworks(data);
        updateDevices(data);
        updateIncidents(data);

        updateTimestamp();

    } catch (error) {

        console.error(
            "Dashboard update failed:",
            error
        );

    }

}


function updateHealth(data) {

    const element =
        document.getElementById(
            "overall-health"
        );

    if (!element) {

        return;

    }

    const healthValue =
        element.querySelector(
            ".health-value"
        );

    const label =
        element.querySelector(
            ".health-label"
        );

    if (!healthValue || !label) {

        return;

    }

    healthValue.classList.remove(
        "state-up",
        "state-down",
        "state-warning"
    );

    healthValue.classList.add(
        data.health.class
    );

    label.textContent =
        data.health.label;

}


function updateService(data) {

    const element =
        document.getElementById(
            "service-state"
        );

    if (!element) {

        return;

    }

    const dot =
        element.querySelector(
            ".status-dot"
        );

    const label =
        element.querySelector(
            ".service-label"
        );

    if (label) {

        label.textContent =
            "Monitoring " +
            data.service.state;

    }

    if (dot) {

        dot.classList.remove(
            "dot-up",
            "dot-down"
        );

        dot.classList.add(
            data.service.up
                ? "dot-up"
                : "dot-down"
        );

    }

}


function updateNetworks(data) {

    for (
        const network
        of data.networks
    ) {

        const card =
            document.querySelector(
                `[data-network="${network.name}"]`
            );

        if (!card) {

            continue;

        }

        const state =
            card.querySelector(
                ".network-state"
            );

        if (state) {

            state.textContent =
                network.healthy
                    ? "HEALTHY"
                    : "ATTENTION";

            state.classList.remove(
                "state-up",
                "state-warning",
                "state-down"
            );

            state.classList.add(
                network.healthy
                    ? "state-up"
                    : "state-warning"
            );

        }

        updateCheck(
            card,
            "gateway",
            network.gateway
        );

        updateCheck(
            card,
            "internet",
            network.internet
        );

        updateCheck(
            card,
            "dns",
            network.dns
        );

    }

}


function updateCheck(
    card,
    type,
    value
) {

    const row =
        card.querySelector(
            `[data-check="${type}"]`
        );

    if (!row || value === null) {

        return;

    }

    const state =
        row.querySelector(
            ".check-state"
        );

    if (!state) {

        return;

    }

    const dot =
        state.querySelector(
            ".status-dot"
        );

    state.textContent =
        "";

    if (dot) {

        state.appendChild(
            dot
        );

    }

    state.appendChild(
        document.createTextNode(
            value
        )
    );

    state.classList.remove(
        "state-up",
        "state-down"
    );

    state.classList.add(
        value === "UP"
            ? "state-up"
            : "state-down"
    );

    if (dot) {

        dot.classList.remove(
            "dot-up",
            "dot-down"
        );

        dot.classList.add(
            value === "UP"
                ? "dot-up"
                : "dot-down"
        );

    }

}


function updateDevices(data) {

    const total =
        document.getElementById(
            "device-total"
        );

    const up =
        document.getElementById(
            "device-up"
        );

    const upLarge =
        document.getElementById(
            "device-up-large"
        );

    const down =
        document.getElementById(
            "device-down"
        );

    const standby =
        document.getElementById(
            "device-standby"
        );

    if (total) {

        total.textContent =
            data.devices.total;

    }

    if (up) {

        up.textContent =
            data.devices.up;

    }

    if (upLarge) {

        upLarge.textContent =
            data.devices.up;

    }

    if (down) {

        down.textContent =
            data.devices.down;

    }

    if (standby) {

        standby.textContent =
            data.devices.standby;

    }

    const list =
        document.getElementById(
            "device-list"
        );

    if (!list) {

        return;

    }

    list.innerHTML = "";

    for (
        const device
        of data.devices.rows
    ) {

        const isStandby =
            device.monitoring_mode === "standby";

        const displayState =
            isStandby
                ? "STANDBY"
                : device.state;

        const row =
            document.createElement(
                "div"
            );

        row.className =
            "device-row";

        const name =
            document.createElement(
                "div"
            );

        name.className =
            "device-name";

        const dot =
            document.createElement(
                "span"
            );

        dot.className =
            "status-dot " +
            (
                isStandby
                    ? "dot-up"
                    : device.state === "UP"
                        ? "dot-up"
                        : "dot-down"
            );

        name.appendChild(
            dot
        );

        name.appendChild(
            document.createTextNode(
                device.name
            )
        );

        const type =
            document.createElement(
                "div"
            );

        type.className =
            "device-type";

        type.textContent =
            device.job_type;

        const state =
            document.createElement(
                "div"
            );

        state.className =
            "device-state " +
            (
                isStandby
                    ? "state-warning"
                    : device.state === "UP"
                        ? "state-up"
                        : "state-down"
            );

        state.textContent =
            displayState;

        row.appendChild(
            name
        );

        row.appendChild(
            type
        );

        row.appendChild(
            state
        );

        list.appendChild(
            row
        );

    }

}


function updateIncidents(data) {

    const list =
        document.getElementById(
            "incident-list"
        );

    const empty =
        document.getElementById(
            "incident-empty"
        );

    if (!list || !empty) {

        return;

    }

    list.innerHTML = "";

    if (
        !data.incidents
        ||
        data.incidents.length === 0
    ) {

        list.style.display = "none";
        empty.style.display = "flex";

        return;

    }

    list.style.display = "block";
    empty.style.display = "none";

    for (
        const incident
        of data.incidents
    ) {

        const item =
            document.createElement(
                "div"
            );

        item.className =
            "incident-item";

        const primary =
            incident.primary;

        const header =
            document.createElement(
                "div"
            );

        header.className =
            "incident-header";

        const title =
            document.createElement(
                "strong"
            );

        title.textContent =
            primary
                ? primary.object
                : "Network incident";

        const duration =
            document.createElement(
                "span"
            );

        duration.textContent =
            formatDuration(
                incident.duration
            );

        header.appendChild(
            title
        );

        header.appendChild(
            duration
        );

        item.appendChild(
            header
        );

        if (primary) {

            const details =
                document.createElement(
                    "div"
                );

            details.className =
                "incident-details";

            details.appendChild(
                createIncidentDetail(
                    "Type",
                    primary.job_type
                )
            );

            details.appendChild(
                createIncidentDetail(
                    "Network",
                    primary.network || "Unknown"
                )
            );

            details.appendChild(
                createIncidentDetail(
                    "Confidence",
                    primary.confidence
                )
            );

            item.appendChild(
                details
            );

        }

        if (
            incident.dependents
            &&
            incident.dependents.length
        ) {

            const dependents =
                document.createElement(
                    "div"
                );

            dependents.className =
                "incident-impact";

            const label =
                document.createElement(
                    "strong"
                );

            label.textContent =
                "Impact: ";

            dependents.appendChild(
                label
            );

            dependents.appendChild(
                document.createTextNode(
                    incident.dependents
                        .map(
                            item =>
                                item.object
                        )
                        .join(
                            ", "
                        )
                )
            );

            item.appendChild(
                dependents
            );

        }

        if (incident.diagnosis) {

            const diagnosis =
                document.createElement(
                    "p"
                );

            diagnosis.className =
                "incident-diagnosis";

            diagnosis.textContent =
                incident.diagnosis;

            item.appendChild(
                diagnosis
            );

        }

        list.appendChild(
            item
        );

    }

}


function createIncidentDetail(
    label,
    value
) {

    const span =
        document.createElement(
            "span"
        );

    span.textContent =
        label +
        ": " +
        value;

    return span;

}


function formatDuration(
    seconds
) {

    if (
        seconds === null
        ||
        seconds === undefined
    ) {

        return "Active";

    }

    const minutes =
        Math.floor(
            seconds / 60
        );

    const remainingSeconds =
        seconds % 60;

    if (minutes) {

        return (
            minutes +
            "m " +
            remainingSeconds +
            "s"
        );

    }

    return (
        remainingSeconds +
        "s"
    );

}


function updateTimestamp() {

    const element =
        document.getElementById(
            "last-updated"
        );

    if (!element) {

        return;

    }

    const now =
        new Date();

    element.textContent =
        "Last updated " +
        now.toLocaleTimeString();

}


updateDashboard();


setInterval(
    updateDashboard,
    5000
);