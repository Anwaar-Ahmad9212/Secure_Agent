"""
log_utils.py  –  shared logging helpers
Both security_proxy.py and logger.py import from here so they
always read/write the SAME logs.json file regardless of cwd.
"""
import json
import os
from datetime import datetime

# Resolve path relative to THIS file (security/ folder)
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
LOGS_FILE = os.path.join(BASE_DIR, "logs.json")


def init_logs_file():
    """Create logs.json if it doesn't exist."""
    if not os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "w") as f:
            json.dump([], f)


def log_event(source, prompt, action, reason="",
              tool="", severity="medium", metadata=None):
    """Append one security event to logs.json."""
    init_logs_file()

    event = {
        "timestamp": datetime.now().isoformat(),
        "source":    source,
        "prompt":    (prompt or "")[:500],
        "action":    action,
        "reason":    reason,
        "tool":      tool,
        "severity":  severity,
        "metadata":  metadata or {},
    }

    try:
        with open(LOGS_FILE, "r") as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        logs = []

    logs.append(event)
    logs = logs[-1000:]          # keep last 1000 entries

    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    print(f"\n[{event['timestamp']}] {action.upper()} | {source}")
    print(f"  Prompt   : {event['prompt'][:80]}...")
    print(f"  Reason   : {reason}")
    print(f"  Severity : {severity}\n")

    return event


def read_logs():
    """Return the full log list (creates file if missing)."""
    init_logs_file()
    try:
        with open(LOGS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def clear_logs():
    """Wipe all logs."""
    with open(LOGS_FILE, "w") as f:
        json.dump([], f)