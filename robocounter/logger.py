from pathlib import Path
from datetime import datetime
import json

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "casomira.log"

MAX_LOG_SIZE = 1024 * 1024  # 1 MB

CONFIG_FILE = BASE_DIR / "data" / "config.json"

def log(msg, level="INFO"):

    try:
        if CONFIG_FILE.exists():
            cfg = json.loads(CONFIG_FILE.read_text())
            if not cfg.get("log_enabled",True):
                return
    except:
        pass    

    try:
        if LOG_FILE.exists():
            if LOG_FILE.stat().st_size > MAX_LOG_SIZE:
                backup = LOG_DIR / "casomira.log.1"
                if backup.exists():
                    backup.unlink()

                LOG_FILE.rename(backup)

    except Exception:
        pass

    try:
        with open(LOG_FILE, "a") as f:
            f.write(
                f"{datetime.now()} {level} {msg}\n"
            )

    except Exception:
        pass