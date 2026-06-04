import json
import subprocess

CONFIG_FILE = "data/config.json"

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def get_wifi_interface():
    try:
        out = subprocess.check_output(
            ["nmcli","-t","-f","DEVICE,TYPE","device"]
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
    subprocess.run(
        [
            "nmcli",
            "connection",
            "up",
            "Hotspot"
        ]
    )

    return True

# =====================================
# CLIENT MODE
# =====================================

def set_client_mode():
    cfg = load_config()
    subprocess.run([
        "nmcli",
        "device",
        "wifi",
        "connect",
        cfg["client_ssid"],
        "password",
        cfg["client_password"]
    ])

    return True

# =====================================
# CHECK CONNECTION
# =====================================

def wifi_connected():
    try:
        result = subprocess.check_output(
            [
                "nmcli",
                "-t",
                "-f",
                "ACTIVE",
                "connection",
                "show"
            ]

        ).decode()
        return "yes" in result

    except:
        return False