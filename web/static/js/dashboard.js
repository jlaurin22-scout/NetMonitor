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

    const dot =
        element.querySelector(
            ".health-dot"
        );

    const label =
        element.querySelector(
            ".health-label"
        );

    element.classList.remove(
        "state-up",
        "state-down",
        "state-warning"
    );

    element.classList.add(
        data.health.class
    );

    label.textContent =
        data.health.label;

    dot.className =
        "health-dot";

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

    label.textContent =
        "Monitoring " +
        data.service.state;

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

        state.textContent =
            network.healthy
                ? "HEALTHY"
                : "ATTENTION";

        state.classList.remove(
            "state-up",
            "state-warning"
        );

        state.classList.add(
            network.healthy
                ? "state-up"
                : "state-warning"
        );

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

    const text =
        state.querySelector(
            ".check-state-text"
        );

    if (text) {

        text.textContent =
            value;

    }

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