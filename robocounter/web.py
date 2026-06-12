from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    Response
)

import requests

import csv
import io
import json
import os
import socket
import subprocess

import wifi_manager

from logger import log

app = Flask(__name__)

# =====================================================
# HELPERS
# =====================================================

def get_ip():

    try:
        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        s.connect(
            ("8.8.8.8", 80)
        )
        ip = s.getsockname()[0]
        s.close()
        return ip

    except:
        return "unknown"

# =====================================================
# PAGE
# =====================================================

@app.route("/")
def index():
    return render_template(
        "index.html"
    )


# =====================================================
# API SERVER
# =====================================================

@app.route("/api/send_result/<int:run_id>", methods=["POST"])
def api_send_result(run_id):

    cfg = app.config["CONFIG"]
    results = app.config["RESULTS"]

    row = next(
        (
            x
            for x in results
            if x["id"] == run_id
        ),
        None
    )

    payload = {
        "gate_id":
            cfg.get(
                "gate_id",
                1
            ),

        "team_id":
            cfg.get(
                "team_id",
                1
            ),

        "id":
            row["id"],

        "time":
            row["time"],

        "timestamp":
            row["timestamp"]
    }

    log(f"API sending results: url={cfg["api_url"]} data={payload} key={cfg["api_key"]}", "DEBUG")

    r = requests.post(
        cfg["api_url"],
        json=payload,
        headers={
            "X-Api-Key":
                cfg["api_key"]
        },
        timeout=10
    )

    if r.status_code == 200:

        row["uploaded"] = True

        with open(
            "data/results.json",
            "w"
        ) as f:
            json.dump(
                results,
                f,
                indent=2
            )

        log(f"API uploaded OK id={run_id}")

        return jsonify({
            "ok": True
        })

    log(f"API uploaded ERR code={r.status_code}")
    return jsonify({
        "ok": False,
        "error":
            f"HTTP {r.status_code}"
    })


# =====================================================
# RESULTS
# =====================================================

@app.route("/api/results")
def api_results():
    data = app.config["RESULTS"]
    cfg = app.config["CONFIG"]
    limit = cfg["web_history_limit"]

    history = list(
        reversed(
            data[-limit:]
        )
    )

    best = min(
        [x["time"] for x in data],
        default=None
    )

    last = (
        data[-1]["time"]
        if data
        else None
    )

    return jsonify({
        "running":
            app.config["STATE"](),

        "current_time":
            app.config["CURRENT_TIME"](),

        "last":
            last,

        "best":
            best,

        "count":
            len(data),

        "results":
            history,

        "api_enabled":
            app.config["CONFIG"].get(
                "api_enabled",
                False
            ),

        "api_auto_send":
            app.config["CONFIG"].get(
                "api_auto_send",
                False
            ),

    })

# =====================================================
# RESET
# =====================================================

@app.route(
    "/api/reset",
    methods=["POST"]
)
def api_reset():
    app.config[
        "RESULTS"
    ].clear()

    log("API results reset", "DEBUG")

    with open(
        "data/results.json",
        "w"
    ) as f:
        f.write("[]")

    return jsonify({
        "ok": True
    })

# =====================================================
# EXPORT CSV
# =====================================================

@app.route("/api/export")
def api_export():
    out = io.StringIO()
    writer = csv.writer(
        out
    )

    writer.writerow([
        "ID",
        "Time",
        "Timestamp"
    ])

    for r in app.config[
        "RESULTS"
    ]:

        writer.writerow([
            r["id"],
            r["time"],
            r["timestamp"]
        ])

    log("API export results.csv", "DEBUG")        

    return Response(
        out.getvalue(),
        mimetype=
        "text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=results.csv"
        }
    )

# =====================================================
# CONFIG
# =====================================================

@app.route("/api/config")
def api_config():
    return jsonify(
        app.config["CONFIG"]
    )

@app.route(
    "/api/config",
    methods=["POST"]
)
def api_save_config():
    cfg = request.json
    app.config[
        "CONFIG"
    ].update(cfg)
    with open(
        "data/config.json",
        "w"
    ) as f:
        json.dump(app.config["CONFIG"],f,indent=2)

    log("API save config", "DEBUG")

    return jsonify({
        "ok": True
    })

# =====================================================
# EXPORT CONFIG
# =====================================================

@app.route(
    "/api/export_config"
)
def api_export_config():
    log("API export config", "DEBUG")
    return Response(
        json.dumps(app.config["CONFIG"],indent=2),
        mimetype=
        "application/json",
        headers={
            "Content-Disposition":
            "attachment; filename=config.json"
        }
    )

# =====================================================
# SYSTEM INFO
# =====================================================

@app.route("/api/system")
def api_system():
    try:
        temp = subprocess.check_output(
            [
                "vcgencmd",
                "measure_temp"
            ]
        ).decode()
    except:
        temp = "unknown"

    try:
        uptime = subprocess.check_output(
            [
                "uptime",
                "-p"
            ]
        ).decode().strip()
    except:
        uptime = "unknown"

    return jsonify({
        "hostname":
            socket.gethostname(),
        "ip":
            get_ip(),
        "uptime":
            uptime,
        "temperature":
            temp
    })

# =====================================================
# RESTART APP
# =====================================================

@app.route(
    "/api/restart_app",
    methods=["POST"]
)
def api_restart_app():
    log("API restart service casomira", "DEBUG")
    result = os.system(
        "sudo systemctl restart casomira"
    )

    return jsonify({
        "ok": result == 0
    })

# =====================================================
# REBOOT PI
# =====================================================

@app.route(
    "/api/reboot",
    methods=["POST"]
)
def api_reboot():
    log("API reboot system", "DEBUG")    
    os.system(
        "sudo reboot"
    )

    return jsonify({
        "ok": True
    })

# =====================================================
# SHUTDOWN PI
# =====================================================

@app.route(
    "/api/shutdown",
    methods=["POST"]
)
def api_shutdown():
    log("API shutdown system", "DEBUG")
    os.system(
        "sudo shutdown -h now"
    )

    return jsonify({
        "ok": True
    })

# =====================================================
# Wi-Fi AP, Client
# =====================================================
@app.route(
    "/api/wifi/ap",
    methods=["POST"]
)
def wifi_ap():

    wifi_manager.set_ap_mode()

    return jsonify(
        {"ok":True}
    )

@app.route(
    "/api/wifi/client",
    methods=["POST"]
)
def wifi_client():

    wifi_manager.set_client_mode()

    return jsonify(
        {"ok":True}
    )