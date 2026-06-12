import json
import time
import threading
import requests

from pathlib import Path
from datetime import datetime

import pigpio

from web import app

from logger import log

import wifi_manager


# =====================================================
# FILES
# =====================================================

DATA_FILE = Path("data/results.json")
CONFIG_FILE = Path("data/config.json")

# =====================================================
# DEFAULT CONFIG
# =====================================================

DEFAULT_CONFIG = {
    "sensor_active_low": False,

    "debounce_ms": 50,
    "min_run_ms": 2500,

    "web_history_limit": 50,
    "max_stored_runs": 5000,

    "buzzer_start_ms": 40,
    "buzzer_stop_ms": 200,

    "wifi_mode": "auto",

    "client_ssid": "",
    "client_password": "",

    "ap_ssid": "CASOMIRA",
    "ap_password": "12345678",

    "api_url": "",
    "api_key": "",
    "api_enabled": False,
    "api_auto_send": False,

    "log_enabled": True,

    "gate_id": 1,
    "team_id": 1,
}

# =====================================================
# GPIO
# =====================================================
SENS  = 20
BUZ   = 12
LASER = 27
LED_R = 25
LED_G = 24

# =====================================================
# LED STATE:
# READY      = GRN
# RUNNING    = blink RED
# FINISHED   = RED 2 s
# =====================================================

# =====================================================
# GLOBALS
# =====================================================
config = {}
results = []
running = False
start_tick = 0
last_tick = 0
current_time = 0
blink_red = False

# =====================================================
# CONFIG
# =====================================================
def load_config():

    global config

    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps(DEFAULT_CONFIG, indent=2)
        )

    try:
        config = json.loads(
            CONFIG_FILE.read_text()
        )
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

    except Exception:
        config = DEFAULT_CONFIG.copy()

def save_config():
    CONFIG_FILE.write_text(
        json.dumps(config, indent=2)
    )

# =====================================================
# RESULTS
# =====================================================

def load_results():

    global results

    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]")

    try:
        results = json.loads(
            DATA_FILE.read_text()
        )

    except Exception:
        results = []

def save_results():

    global results
    max_runs = config["max_stored_runs"]
    if len(results) > max_runs:
        results = results[-max_runs:]

    DATA_FILE.write_text(
        json.dumps(results, indent=2)
    )

log("====================================")
log("CASOMIRA START")
log("Verze 2.0")

# =====================================================
# GPIO
# =====================================================

pi = pigpio.pi()

if not pi.connected:
    log("pigpiod not running. Type: sudo pigpiod", "ERROR")
    raise RuntimeError(
        "pigpiod not running. Type: sudo pigpiod"
    )

for pin in [
    BUZ,
    LASER,
    LED_R,
    LED_G,
    #LED_B
]:

    pi.set_mode(
        pin,
        pigpio.OUTPUT
    )

pi.set_mode(
    SENS,
    pigpio.INPUT
)

pi.set_pull_up_down(
    SENS,
    pigpio.PUD_UP
)

pi.set_glitch_filter(
    SENS,
    10000
)

# =====================================================
# LED
# =====================================================

def led_off():
    pi.write(LED_R, 1)
    pi.write(LED_G, 1)

def led_ready():
    pi.write(LED_R, 1)
    pi.write(LED_G, 0)

def led_finished():
    pi.write(LED_R, 0)
    pi.write(LED_G, 1)

def led_running_start():
    global blink_red
    blink_red = True 

def led_running_stop():
    global blink_red
    blink_red = False
    pi.write(
        LED_R,
        1
    )

def led_blink_thread():
    state = False
    while True:
        if blink_red:
            state = not state
            pi.write(
                LED_R,
                0 if state else 1
            )
        time.sleep(0.25)


def wifi_led_sta_try():
    # rychlé zelené blikání
    pass

def wifi_led_sta_ok():
    # trvale zelená
    pass

def wifi_led_ap_start():
    # rychlé červené blikání
    pass

def wifi_led_ap_ok():
    # střídání červená/zelená
    pass                  

# =====================================================
# BUZZER
# =====================================================

def beep(ms, freq=2500):
    pi.set_PWM_frequency(
        BUZ,
        freq
    )

    pi.set_PWM_dutycycle(
        BUZ,
        128
    )

    time.sleep(
        ms / 1000
    )

    pi.set_PWM_dutycycle(
        BUZ,
        0
    )

# =====================================================
# SENSOR
# =====================================================

startup_time = time.time()

def sensor_cb(gpio, level, tick):

    if time.time() - startup_time < 2:
        return

    global running
    global start_tick
    global last_tick

    beep(20)

    debounce_us = config["debounce_ms"] * 1000

    if pigpio.tickDiff(
        last_tick,
        tick
    ) < debounce_us:

        return

    last_tick = tick

    # START
    if not running:
        running = True
        log("START")
        start_tick = tick
        led_running_start()
        beep(
            config["buzzer_start_ms"]
        )
        return

    elapsed_ms = pigpio.tickDiff(
        start_tick,
        tick
    ) / 1000

    if elapsed_ms < config["min_run_ms"]:
        log(
            f"STOP ignored ({elapsed_ms:.0f} ms)"
        )        
        return

    # STOP
    running = False

    diff = pigpio.tickDiff(
        start_tick,
        tick
    )

    seconds = round(
        diff / 1_000_000,
        2
    )

    next_id = (
        results[-1]["id"] + 1
        if results
        else 1
    )

    results.append({
        "id": next_id,
        "time": seconds,
        "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        "uploaded": False
    })

    save_results()
    
    # =====================================
    # AUTO API SEND
    # =====================================

    if (config.get(
            "api_enabled",
            False
        )
        and
        config.get(
            "api_auto_send",
            False
        )
    ):
        try:
            requests.post(
                f"http://127.0.0.1:5000/api/send_result/{next_id}",
                timeout=10
            )

        except Exception as e:
            log(f"AUTO API send ERROR: {e}")

    led_running_stop()
    led_finished()

    log(
        f"RESULT id={next_id} "
        f"time={seconds}"
    )

    threading.Timer(
        2,
        led_ready
    ).start()

    beep(
        config["buzzer_stop_ms"]
    )

# =====================================================
# TIMER THREAD
# =====================================================

def timer_thread():

    global current_time

    while True:
        if running:
            current_time = round(
                pigpio.tickDiff(
                    start_tick,
                    pi.get_current_tick()
                ) / 1_000_000,
                2
            )

        time.sleep(0.05)

# =====================================================
# INIT
# =====================================================

load_config()

log(
    f"Config: "
    f"wifi_mode={config['wifi_mode']} "
    f"client_ssid={config['client_ssid']} "
    f"ap_ssid={config['ap_ssid']}"
)

load_results()

pi.write(LASER, 1)

time.sleep(1)

last_tick = pi.get_current_tick()

EDGE = (
    pigpio.FALLING_EDGE
    if config["sensor_active_low"]
    else
    pigpio.RISING_EDGE
)

cb = pi.callback(
    SENS,
    EDGE,
    sensor_cb
)



led_ready()

for _ in range(3):
    beep(100)
    time.sleep(0.1)

# =====================================================
# WEB
# =====================================================

app.config["RESULTS"] = results
app.config["CONFIG"] = config
app.config["STATE"] = lambda: running
app.config["CURRENT_TIME"] = lambda: current_time

threading.Thread(
    target=timer_thread,
    daemon=True
).start()

threading.Thread(
    target=led_blink_thread,
    daemon=True
).start()

web_thread = threading.Thread(
    target=lambda: app.run(
        host="127.0.0.1",
        port=5000,
        use_reloader=False
    ),
    daemon=True
)

web_thread.start()

log("Waiting for WiFi...")

for i in range(30):
    iface = wifi_manager.get_wifi_interface()
    if iface:
        break
    time.sleep(1)

ENABLE_WIFI_MANAGER = True

if ENABLE_WIFI_MANAGER:
    iface = wifi_manager.get_wifi_interface()
    if iface is not None:
        mode = config["wifi_mode"]
        log(f"WiFi mode: {mode}")
        # =====================
        # AP
        # =====================
        if mode == "ap":
            wifi_manager.set_ap_mode()
        # =====================
        # CLIENT
        # =====================
        elif mode == "client":
            wifi_led_sta_try()
            wifi_manager.set_client_mode()
        # =====================
        # AUTO
        # =====================
        elif mode == "auto":
            log("Trying client mode...")
            wifi_manager.set_client_mode()

            for _ in range(30):
                if wifi_manager.wifi_client_connected():
                    wifi_led_sta_ok()
                    log("STA connected")
                    break
                time.sleep(1)
            else:
                log("STA failed -> AP")
                wifi_led_ap_start()
                wifi_manager.set_ap_mode()
                wifi_led_ap_ok()
    else:
        log("No WiFi interface detected")

# =====================================================
# LOOP
# =====================================================

while True:
    time.sleep(1)