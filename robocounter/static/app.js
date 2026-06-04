let currentData = null;

// =====================================
// LOAD RESULTS
// =====================================

async function loadResults()
{
    try
    {
        const r = await fetch(
            "/api/results"
        );
        const data = await r.json();
        currentData = data;
        updateDashboard(data);
    }
    catch(err)
    {
        console.error(err);
    }
}

// =====================================
// UPDATE UI
// =====================================

function updateDashboard(data)
{
    document.getElementById(
        "status"
    ).innerText =
        data.running
        ? "MĚŘENÍ"
        : "PŘIPRAVEN";

    let display = "0.00";

    if(data.running)
    {
        display =
            Number(
                data.current_time
            ).toFixed(2);
    }
    else
    {
        if(data.last !== null)
        {
            display =
                Number(
                    data.last
                ).toFixed(2);
        }
    }

    document.getElementById(
        "bigTimer"
    ).innerText = display;

    document.getElementById(
        "last"
    ).innerText =
        data.last ?? "-";

    document.getElementById(
        "best"
    ).innerText =
        data.best ?? "-";

    document.getElementById(
        "count"
    ).innerText =
        data.count;    

    let html = "";

    data.results.forEach(
        row =>
        {
            html += `
            <tr>
                <td>${row.id}</td>
                <td>${row.time}</td>
                <td>${row.timestamp}</td>
            </tr>
            `;
        }
    );

    document.getElementById(
        "historyBody"
    ).innerHTML = html;
}

// =====================================
// FULLSCREEN
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    () =>
    {
        document
        .getElementById(
            "bigTimer"
        )
        .addEventListener(
            "click",
            toggleFullscreen
        );

        document
        .getElementById(
            "btnSettings"
        )
        .addEventListener(
            "click",
            openSettings
        );

        loadResults();

        setInterval(
            loadResults,
            500
        );
    }
);

function toggleFullscreen()
{
    const el =
        document.getElementById(
            "bigTimer"
        );

    if(
        !document.fullscreenElement
    )
    {
        el.requestFullscreen();
    }
    else
    {
        document.exitFullscreen();
    }
}

// =====================================
// SETTINGS
// =====================================

async function openSettings()
{
    document
    .getElementById(
        "settingsModal"
    )
    .style.display = "block";

    await loadConfig();

    await loadSystem();
}

function closeSettings()
{
    document
    .getElementById(
        "settingsModal"
    )
    .style.display = "none";
}

// =====================================
// CONFIG
// =====================================

async function loadConfig()
{
    const r =
        await fetch(
            "/api/config"
        );

    const cfg =
        await r.json();

    document
    .getElementById(
        "sensor_active_low"
    ).checked =
        cfg.sensor_active_low;

    document
    .getElementById(
        "debounce_ms"
    ).value =
        cfg.debounce_ms;

    document
    .getElementById(
        "min_run_ms"
    ).value = 
        cfg.min_run_ms;        

    document
    .getElementById(
        "buzzer_start_ms"
    ).value =
        cfg.buzzer_start_ms;

    document
    .getElementById(
        "buzzer_stop_ms"
    ).value =
        cfg.buzzer_stop_ms;

    document
    .getElementById(
        "wifi_mode"
    ).value =
        cfg.wifi_mode;

    document
    .getElementById(
        "wifi_ssid"
    ).value =
        cfg.wifi_ssid;

    document
    .getElementById(
        "wifi_password"
    ).value =
        cfg.wifi_password;
}

async function saveConfig()
{
    const cfg =
    {
        sensor_active_low:
            document
            .getElementById(
                "sensor_active_low"
            ).checked,

        debounce_ms:
            parseInt(
                document
                .getElementById(
                    "debounce_ms"
                ).value
            ),

        min_run_ms: 
            parseInt(
                document
                .getElementById(
                    "min_run_ms"
                ).value
            ),

        buzzer_start_ms:
            parseInt(
                document
                .getElementById(
                    "buzzer_start_ms"
                ).value
            ),

        buzzer_stop_ms:
            parseInt(
                document
                .getElementById(
                    "buzzer_stop_ms"
                ).value
            ),

        wifi_mode:
            document
            .getElementById(
                "wifi_mode"
            ).value,

        wifi_ssid:
            document
            .getElementById(
                "wifi_ssid"
            ).value,

        wifi_password:
            document
            .getElementById(
                "wifi_password"
            ).value
    };

    await fetch(
        "/api/config",
        {
            method:"POST",
            headers:
            {
                "Content-Type":
                "application/json"
            },
            body:
            JSON.stringify(cfg)
        }
    );

    alert(
        "Konfigurace uložena"
    );
}

// =====================================
// SYSTEM
// =====================================

async function loadSystem()
{
    const r =
        await fetch(
            "/api/system"
        );

    const s =
        await r.json();

    document
    .getElementById(
        "systemInfo"
    )
    .innerHTML =
    `
    <p>Hostname: ${s.hostname}</p>
    <p>IP: ${s.ip}</p>
    <p>Uptime: ${s.uptime}</p>
    <p>CPU: ${s.temperature}</p>
    `;
}

// =====================================
// RESET
// =====================================

async function resetResults()
{
    if(
        !confirm(
            "Opravdu smazat historii?"
        )
    )
    {
        return;
    }

    await fetch(
        "/api/reset",
        {
            method:"POST"
        }
    );

    loadResults();
}

// =====================================
// EXPORT
// =====================================

function exportCSV()
{
    window.location =
        "/api/export";
}

function exportConfig()
{
    window.location =
        "/api/export_config";
}

// =====================================
// SYSTEM ACTIONS
// =====================================

async function restartApp()
{
    if(
        confirm(
            "Restart aplikace?"
        )
    )
    {
        await fetch(
            "/api/restart_app",
            {
                method:"POST"
            }
        );
    }
}

async function rebootPi()
{
    if(
        confirm(
            "Restart Raspberry?"
        )
    )
    {
        await fetch(
            "/api/reboot",
            {
                method:"POST"
            }
        );
    }
}

async function shutdownPi()
{
    if(
        confirm(
            "Vypnout Raspberry?"
        )
    )
    {
        await fetch(
            "/api/shutdown",
            {
                method:"POST"
            }
        );
    }
}

// =====================================
// TABS
// =====================================

function showTab(tab)
{
    document
    .querySelectorAll(".tab")
    .forEach(
        t => t.classList.add(
            "hidden"
        )
    );

    document
    .getElementById(
        "tab_" + tab
    )
    .classList.remove(
        "hidden"
    );
}