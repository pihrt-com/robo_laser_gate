let currentData = null;
let currentConfig = null;

// =====================================
// SAVE TEAM from home
// =====================================
async function saveTeamId()
{
    const cfg =
    {
        team_id:
            parseInt(
                document
                .getElementById(
                    "team_id"
                ).value
            )
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
}

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
        "apiHeader"
    ).style.display =
        data.api_enabled
        ? ""
        : "none";

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
            let btn = "";

            if(row.time < 10)
            {
                btn =
                `
                <button
                    disabled
                    class="btn-api-disabled">
                    ---
                </button>
                `;
            }
            else if(row.uploaded)
            {
                btn =
                `
                <button
                    disabled
                    class="btn-api-sent">
                    ODESLÁNO
                </button>
                `;
            }
            else if(data.api_auto_send)
            {
                btn =
                `
                <span class="api-wait">
                    ČEKÁ
                </span>
                `;
            }
            else
            {
                btn =
                `
                <button
                    onclick="sendToApi(${row.id})"
                    class="btn-api">
                    ODESLAT
                </button>
                `;
            }

            html += `
            <tr>
                <td>${row.id}</td>
                <td>${row.time}</td>
                <td>${row.timestamp}</td>
                ${data.api_enabled ? `<td>${btn}</td>` : ""}
            </tr>
            `;
        }
    );

    document.getElementById(
        "historyBody"
    ).innerHTML = html;

    document.getElementById(
        "gateDisplay"
    )
    .innerText =
        currentConfig
        ? currentConfig.gate_id
        : "-";    
}

// =====================================
// FULLSCREEN
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    async () =>
    {
        document.getElementById(
            "bigTimer"
        )
        .addEventListener(
            "click",
            toggleFullscreen
        );

        document.getElementById(
            "btnSettings"
        )
        .addEventListener(
            "click",
            openSettings
        );

        const gate =
        document.getElementById(
            "gate_id"
        );

        const team =
        document.getElementById(
            "team_id"
        );

        for(let i=1;i<=20;i++)
        {
            const o =
                document.createElement(
                    "option"
                );

            o.value = i;
            o.textContent = i;

            gate.appendChild(o);
        }

        for(let i=1;i<=100;i++)
        {
            const o =
                document.createElement(
                    "option"
                );

            o.value = i;
            o.textContent = i;

            team.appendChild(o);
        }        

        await loadConfig();

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

    document.getElementById(
        "sensor_active_low"
    ).checked =
        cfg.sensor_active_low;

    document.getElementById(
        "debounce_ms"
    ).value =
        cfg.debounce_ms;

    document.getElementById(
        "min_run_ms"
    ).value = 
        cfg.min_run_ms;        

    document.getElementById(
        "buzzer_start_ms"
    ).value =
        cfg.buzzer_start_ms;

    document.getElementById(
        "buzzer_stop_ms"
    ).value =
        cfg.buzzer_stop_ms;

    document.getElementById(
        "wifi_mode"
    ).value =
        cfg.wifi_mode;

    document.getElementById(
        "client_ssid"
    ).value =
        cfg.client_ssid || "";

    document.getElementById(
        "client_password"
    ).value =
        cfg.client_password || "";

    document.getElementById(
        "ap_ssid"
    ).value =
        cfg.ap_ssid || "CASOMIRA";

    document.getElementById(
        "ap_password"
    ).value =
        cfg.ap_password || "12345678";

    document.getElementById(
        "api_url"
    ).value =
        cfg.api_url || "";

    document.getElementById(
        "api_key"
    ).value =
        cfg.api_key || "";

    document.getElementById(
        "log_enabled"
    ).checked =
        cfg.log_enabled ?? true;

    document.getElementById(
        "gate_id"
    ).value =
        cfg.gate_id || 1;

    document.getElementById(
        "team_id"
    ).value =
        cfg.team_id || 1;

    document.getElementById(
        "api_enabled"
    ).checked =
        cfg.api_enabled ?? false;

    document.getElementById(
        "api_auto_send"
    ).checked =
        cfg.api_auto_send ?? false;        

    currentConfig = cfg;         
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

        client_ssid:
            document
            .getElementById(
                "client_ssid"
            ).value,

        client_password:
            document
            .getElementById(
                "client_password"
            ).value,

        ap_ssid:
            document
            .getElementById(
                "ap_ssid"
            ).value,

        ap_password:
            document
            .getElementById(
                "ap_password"
            ).value,

        api_url:
            document
            .getElementById(
                "api_url"
            )
            .value,

        api_key:
            document
            .getElementById(
                "api_key"
            )
            .value, 

        log_enabled:
            document
            .getElementById(
                "log_enabled"
            )
            .checked,

        gate_id:
            parseInt(
                document
                .getElementById(
                    "gate_id"
                ).value
            ),

        api_enabled:
            document
            .getElementById(
                "api_enabled"
            )
            .checked,

        api_auto_send:
            document
            .getElementById(
                "api_auto_send"
            )
            .checked,
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
        "Konfigurace uložena. Aplikace bude restartována."
    );

    restartApp();
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
    <p>Martin Pihrt (www.pihrt.com)</p>
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

function showTab(
    tab,
    btn
)
{
    document
    .querySelectorAll(".tab")
    .forEach(
        t => t.classList.add(
            "hidden"
        )
    );

    document
    .querySelectorAll(
        ".tab-btn"
    )
    .forEach(
        b => b.classList.remove(
            "active"
        )
    );

    document
    .getElementById(
        "tab_" + tab
    )
    .classList.remove(
        "hidden"
    );

    if(btn)
    {
        btn.classList.add(
            "active"
        );
    }
}

// =====================================
// SEND API
// =====================================

async function sendToApi(id)
{
    const r = await fetch(
        "/api/send_result/" + id,
        {
            method: "POST"
        }
    );

    const data = await r.json();

    if(data.ok)
    {
        loadResults();
    }
    else
    {
        alert(
            data.error || "Chyba API"
        );
    }
}