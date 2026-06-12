import json
import subprocess

from logger import log

CONFIG_FILE = "data/config.json"

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def wifi_client_connected():
    try:
        out = subprocess.check_output(
            [   "sudo",
                "nmcli",
                "-t",
                "-f",
                "DEVICE,TYPE,STATE",
                "device"
            ]
        ).decode()

        for line in out.splitlines():
            dev, typ, state = line.split(":")
            if typ == "wifi" and state == "connected":
                log(
                    f"Connected: {dev}"
                )                
                return True
        log(
            "No WiFi connection"
        )

    except:
        pass

    return False


def get_wifi_interface():
    try:
        out = subprocess.check_output(
            [
                "sudo",
                "nmcli",
                "-t",
                "-f",
                "DEVICE,TYPE",
                "device"
            ]
        ).decode()

        for line in out.splitlines():
            dev, typ = line.split(":")
            if typ == "wifi":
                return dev

    except:
        pass

    return None

# =====================================
# AP MODE
# =====================================

def set_ap_mode():
    try:
        cfg = load_config()
        ssid = cfg["ap_ssid"]
        password = cfg["ap_password"]

        log(f"AP mode: SSID={ssid}")

        result = subprocess.run(
            [   "sudo",
                "nmcli",
                "connection",
                "modify",
                "Hotspot",
                "802-11-wireless.ssid",
                ssid
            ],
            capture_output=True,
            text=True
        )

        log(
            f"AP set SSID rc={result.returncode} "
            f"out={result.stdout.strip()} "
            f"err={result.stderr.strip()}"
        )

        result = subprocess.run(
            [   "sudo",
                "nmcli",
                "connection",
                "modify",
                "Hotspot",
                "802-11-wireless-security.psk",
                password
            ],
            capture_output=True,
            text=True
        )

        log(
            f"AP set PSK rc={result.returncode} "
            f"out={result.stdout.strip()} "
            f"err={result.stderr.strip()}"
        )

        result = subprocess.run(
            [   "sudo",
                "nmcli",
                "connection",
                "up",
                "Hotspot"
            ],
            capture_output=True,
            text=True
        )

        log(
            f"AP start rc={result.returncode} "
            f"out={result.stdout.strip()} "
            f"err={result.stderr.strip()}"
        )

        return True

    except Exception as e:
        log(f"AP ERROR: {e}") 
        return False       

# =====================================
# CLIENT MODE
# =====================================

def set_client_mode():

    cfg = load_config()

    log(f"STA mode: SSID={cfg['client_ssid']}")

    result = subprocess.run(
        [   "sudo",
            "nmcli",
            "connection",
            "delete",
            "RoboCounterSTA"
        ],
        capture_output=True,
        text=True
    )

    log(
        f"STA delete rc={result.returncode} "
        f"out={result.stdout.strip()} "
        f"err={result.stderr.strip()}"
    )

    result = subprocess.run(
        [   "sudo",
            "nmcli",
            "device",
            "wifi",
            "connect",
            cfg["client_ssid"],
            "password",
            cfg["client_password"],
            "name",
            "RoboCounterSTA"
        ],
        capture_output=True,
        text=True
    )

    log(
        f"STA connect rc={result.returncode} "
        f"out={result.stdout.strip()} "
        f"err={result.stderr.strip()}"
    )

    return result.returncode == 0