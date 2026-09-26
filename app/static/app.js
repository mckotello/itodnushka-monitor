const API_URL = "/api";

let currentMonitorId = null;
let currentPeriod = "1h";


const monitorsContainer = document.getElementById(
    "monitorsContainer"
);

const totalMonitors = document.getElementById(
    "totalMonitors"
);

const upMonitors = document.getElementById(
    "upMonitors"
);

const downMonitors = document.getElementById(
    "downMonitors"
);

const unknownMonitors = document.getElementById(
    "unknownMonitors"
);

const refreshButton = document.getElementById(
    "refreshButton"
);

const addMonitorButton = document.getElementById(
    "addMonitorButton"
);

const monitorModal = document.getElementById(
    "monitorModal"
);

const closeModalButton = document.getElementById(
    "closeModalButton"
);

const monitorForm = document.getElementById(
    "monitorForm"
);

const monitorName = document.getElementById(
    "monitorName"
);

const monitorUrl = document.getElementById(
    "monitorUrl"
);

const formError = document.getElementById(
    "formError"
);


const detailsModal = document.getElementById(
    "detailsModal"
);

const closeDetailsButton = document.getElementById(
    "closeDetailsButton"
);

const detailsTitle = document.getElementById(
    "detailsTitle"
);

const detailsUrl = document.getElementById(
    "detailsUrl"
);

const detailUptime = document.getElementById(
    "detailUptime"
);

const detailChecks = document.getElementById(
    "detailChecks"
);

const detailAverage = document.getElementById(
    "detailAverage"
);

const detailMin = document.getElementById(
    "detailMin"
);

const detailMax = document.getElementById(
    "detailMax"
);

const historyContainer = document.getElementById(
    "historyContainer"
);

const chart = document.getElementById(
    "responseChart"
);

const chartContext = chart.getContext("2d");


function escapeHtml(value) {
    const div = document.createElement("div");

    div.textContent = value ?? "";

    return div.innerHTML;
}


function getStatusClass(status) {
    if (status === "up") {
        return "status-up";
    }

    if (status === "down") {
        return "status-down";
    }

    return "status-unknown";
}


function getStatusText(status) {
    if (status === "up") {
        return "Работает";
    }

    if (status === "down") {
        return "Недоступен";
    }

    return "Не проверялся";
}


function formatResponseTime(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    return `${value} мс`;
}


function formatDate(value) {
    if (!value) {
        return "—";
    }

    return new Date(value).toLocaleString(
        "ru-RU"
    );
}


function updateSummary(monitors) {
    totalMonitors.textContent =
        monitors.length;

    upMonitors.textContent =
        monitors.filter(
            monitor =>
                monitor.last_status === "up"
        ).length;

    downMonitors.textContent =
        monitors.filter(
            monitor =>
                monitor.last_status === "down"
        ).length;

    unknownMonitors.textContent =
        monitors.filter(
            monitor =>
                !monitor.last_status
        ).length;
}


function renderMonitors(monitors) {
    if (!monitors.length) {
        monitorsContainer.innerHTML = `
            <div class="empty">
                Пока нет ни одного монитора.
            </div>
        `;

        return;
    }


    monitorsContainer.innerHTML = monitors
        .map(monitor => {

            const statusClass =
                getStatusClass(
                    monitor.last_status
                );

            const statusText =
                getStatusText(
                    monitor.last_status
                );


            return `
                <article class="monitor">

                    <div class="monitor-main">

                        <div class="monitor-name">
                            ${escapeHtml(
                                monitor.name
                            )}
                        </div>

                        <div class="monitor-url">
                            ${escapeHtml(
                                monitor.url
                            )}
                        </div>

                    </div>


                    <div>
                        <span
                            class="status ${statusClass}"
                        >
                            ${statusText}
                        </span>
                    </div>


                    <div class="monitor-value">

                        <span
                            class="monitor-value-label"
                        >
                            Ответ
                        </span>

                        <strong>
                            ${formatResponseTime(
                                monitor.last_response_time_ms
                            )}
                        </strong>

                    </div>


                    <div class="monitor-value">

                        <span
                            class="monitor-value-label"
                        >
                            Последняя проверка
                        </span>

                        <strong>
                            ${formatDate(
                                monitor.last_checked_at
                            )}
                        </strong>

                    </div>


                    <div class="monitor-actions">

                        <button
                            class="button"
                            onclick="openDetails(
                                ${monitor.id}
                            )"
                        >
                            Подробнее
                        </button>

                        <button
                            class="button"
                            onclick="runCheck(
                                ${monitor.id}
                            )"
                        >
                            Проверить
                        </button>

                    </div>

                </article>
            `;
        })
        .join("");
}


async function loadMonitors() {
    try {

        const response = await fetch(
            `${API_URL}/monitors`
        );

        if (!response.ok) {
            throw new Error(
                "Не удалось загрузить мониторы"
            );
        }

        const monitors =
            await response.json();

        updateSummary(monitors);
        renderMonitors(monitors);

    } catch (error) {

        monitorsContainer.innerHTML = `
            <div class="empty">
                Ошибка загрузки данных.
            </div>
        `;

        console.error(error);
    }
}


async function runCheck(id) {
    try {

        const response = await fetch(
            `${API_URL}/monitors/${id}/check`,
            {
                method: "POST",
            }
        );

        if (!response.ok) {
            throw new Error(
                "Ошибка проверки монитора"
            );
        }

        await loadMonitors();

    } catch (error) {

        console.error(error);

        alert(
            "Не удалось выполнить проверку."
        );
    }
}


async function openDetails(id) {
    currentMonitorId = id;

    currentPeriod = "1h";

    detailsModal.classList.remove(
        "hidden"
    );

    setActivePeriodButton();

    try {

        const monitorResponse =
            await fetch(
                `${API_URL}/monitors/${id}`
            );

        if (!monitorResponse.ok) {
            throw new Error(
                "Монитор не найден"
            );
        }

        const monitor =
            await monitorResponse.json();

        detailsTitle.textContent =
            monitor.name;

        detailsUrl.textContent =
            monitor.url;

        await loadDetails();

    } catch (error) {

        console.error(error);

        historyContainer.innerHTML =
            "Не удалось загрузить данные.";
    }
}


async function loadDetails() {
    if (!currentMonitorId) {
        return;
    }


    const statsResponse =
        await fetch(
            `${API_URL}/monitors/` +
            `${currentMonitorId}/stats` +
            `?period=${currentPeriod}`
        );


    if (!statsResponse.ok) {
        throw new Error(
            "Не удалось загрузить статистику"
        );
    }


    const stats =
        await statsResponse.json();


    detailUptime.textContent =
        `${stats.uptime_percent}%`;

    detailChecks.textContent =
        stats.total_checks;

    detailAverage.textContent =
        formatResponseTime(
            stats.average_response_time_ms
        );

    detailMin.textContent =
        formatResponseTime(
            stats.min_response_time_ms
        );

    detailMax.textContent =
        formatResponseTime(
            stats.max_response_time_ms
        );


    const historyResponse =
        await fetch(
            `${API_URL}/monitors/` +
            `${currentMonitorId}/history` +
            "?limit=100"
        );


    if (!historyResponse.ok) {
        throw new Error(
            "Не удалось загрузить историю"
        );
    }


    const history =
        await historyResponse.json();


    renderHistory(history);
    drawChart(history);
}


function renderHistory(history) {

    if (!history.length) {

        historyContainer.innerHTML = `
            <div class="empty">
                Проверок пока нет.
            </div>
        `;

        return;
    }


    historyContainer.innerHTML = `
        <table class="history-table">

            <thead>
                <tr>
                    <th>Время</th>
                    <th>Статус</th>
                    <th>HTTP</th>
                    <th>Ответ</th>
                    <th>Ошибка</th>
                </tr>
            </thead>

            <tbody>

                ${history.map(item => `

                    <tr>

                        <td>
                            ${formatDate(
                                item.checked_at
                            )}
                        </td>

                        <td>
                            <span
                                class="
                                    history-status
                                    ${item.status}
                                "
                            >
                                ${
                                    item.status ===
                                    "up"
                                        ? "UP"
                                        : "DOWN"
                                }
                            </span>
                        </td>

                        <td>
                            ${
                                item.status_code ??
                                "—"
                            }
                        </td>

                        <td>
                            ${formatResponseTime(
                                item.response_time_ms
                            )}
                        </td>

                        <td>
                            ${
                                escapeHtml(
                                    item.error_message
                                ) || "—"
                            }
                        </td>

                    </tr>

                `).join("")}

            </tbody>

        </table>
    `;
}


function drawChart(history) {

    const width =
        chart.clientWidth;

    const height = 280;

    const deviceRatio =
        window.devicePixelRatio || 1;


    chart.width =
        width * deviceRatio;

    chart.height =
        height * deviceRatio;


    chartContext.setTransform(
        deviceRatio,
        0,
        0,
        deviceRatio,
        0,
        0
    );


    chartContext.clearRect(
        0,
        0,
        width,
        height
    );


    if (!history.length) {
        return;
    }


    const points =
        [...history]
            .reverse()
            .filter(
                item =>
                    item.response_time_ms !== null
            );


    if (!points.length) {
        return;
    }


    const values =
        points.map(
            item =>
                item.response_time_ms
        );


    const maxValue =
        Math.max(...values, 1);

    const padding = 30;

    const graphWidth =
        width - padding * 2;

    const graphHeight =
        height - padding * 2;


    // Grid

    chartContext.lineWidth = 1;


    for (let i = 0; i <= 4; i++) {

        const y =
            padding +
            (graphHeight / 4) * i;


        chartContext.beginPath();

        chartContext.moveTo(
            padding,
            y
        );

        chartContext.lineTo(
            width - padding,
            y
        );

        chartContext.stroke();
    }


    // Line

    chartContext.beginPath();


    points.forEach(
        (point, index) => {

            const x =
                padding +
                (
                    index /
                    Math.max(
                        points.length - 1,
                        1
                    )
                ) *
                graphWidth;


            const y =
                height -
                padding -
                (
                    point.response_time_ms /
                    maxValue
                ) *
                graphHeight;


            if (index === 0) {
                chartContext.moveTo(
                    x,
                    y
                );
            } else {
                chartContext.lineTo(
                    x,
                    y
                );
            }
        }
    );


    chartContext.lineWidth = 3;

    chartContext.stroke();


    // Labels

    chartContext.font =
        "12px sans-serif";


    chartContext.fillText(
        `${maxValue} мс`,
        5,
        padding
    );


    chartContext.fillText(
        "0 мс",
        5,
        height - padding
    );
}


function setActivePeriodButton() {

    document
        .querySelectorAll(
            ".period-button"
        )
        .forEach(button => {

            button.classList.toggle(
                "active",
                button.dataset.period ===
                currentPeriod
            );
        });
}


document
    .querySelectorAll(
        ".period-button"
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            async () => {

                currentPeriod =
                    button.dataset.period;

                setActivePeriodButton();

                try {
                    await loadDetails();
                } catch (error) {
                    console.error(error);
                }
            }
        );
    });


function openModal() {

    formError.classList.add(
        "hidden"
    );

    monitorForm.reset();

    monitorModal.classList.remove(
        "hidden"
    );

    monitorName.focus();
}


function closeModal() {
    monitorModal.classList.add(
        "hidden"
    );
}


function closeDetails() {
    detailsModal.classList.add(
        "hidden"
    );

    currentMonitorId = null;
}


monitorForm.addEventListener(
    "submit",
    async event => {

        event.preventDefault();

        formError.classList.add(
            "hidden"
        );


        const payload = {
            name: monitorName.value.trim(),
            url: monitorUrl.value.trim(),
        };


        try {

            const response =
                await fetch(
                    `${API_URL}/monitors`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/json",
                        },
                        body:
                            JSON.stringify(
                                payload
                            ),
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "Не удалось создать монитор"
                );
            }


            closeModal();

            await loadMonitors();

        } catch (error) {

            formError.textContent =
                error.message;

            formError.classList.remove(
                "hidden"
            );
        }
    }
);


addMonitorButton.addEventListener(
    "click",
    openModal
);


closeModalButton.addEventListener(
    "click",
    closeModal
);


closeDetailsButton.addEventListener(
    "click",
    closeDetails
);


refreshButton.addEventListener(
    "click",
    loadMonitors
);


monitorModal.addEventListener(
    "click",
    event => {

        if (
            event.target ===
            monitorModal
        ) {
            closeModal();
        }
    }
);


detailsModal.addEventListener(
    "click",
    event => {

        if (
            event.target ===
            detailsModal
        ) {
            closeDetails();
        }
    }
);


window.addEventListener(
    "resize",
    () => {

        if (
            currentMonitorId &&
            !detailsModal.classList.contains(
                "hidden"
            )
        ) {
            loadDetails().catch(
                console.error
            );
        }
    }
);


loadMonitors();


setInterval(
    loadMonitors,
    30000
);