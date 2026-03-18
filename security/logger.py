#!/usr/bin/env python3
"""
Security Event Logger  –  Flask API on port 5002
Reads logs written by log_utils.py and serves them to the dashboard.
"""
import os, sys
from flask import Flask, jsonify
from flask_cors import CORS

# Import shared helpers so we always point at the same logs.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from log_utils import read_logs, clear_logs, LOGS_FILE   # noqa

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Logger API is running",
        "endpoints": ["/logs", "/logs/recent", "/alerts", "/stats", "/health"]
    })


@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(read_logs())


@app.route("/logs/recent", methods=["GET"])
def get_recent_logs():
    return jsonify(read_logs()[-50:])


@app.route("/alerts", methods=["GET"])
def get_alerts():
    logs = read_logs()
    return jsonify([l for l in logs if l.get("action") == "blocked"][-50:])


@app.route("/stats", methods=["GET"])
def get_stats():
    logs  = read_logs()
    total = len(logs)
    blocked = sum(1 for l in logs if l.get("action") == "blocked")
    allowed = sum(1 for l in logs if l.get("action") == "allowed")

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    source_counts   = {}
    for l in logs:
        sev = l.get("severity", "medium")
        if sev in severity_counts:
            severity_counts[sev] += 1
        src = l.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1

    return jsonify({
        "total_requests":  total,
        "blocked":         blocked,
        "allowed":         allowed,
        "block_rate":      round(blocked / total * 100, 2) if total else 0,
        "severity_counts": severity_counts,
        "source_counts":   source_counts,
    })


@app.route("/clear", methods=["POST"])
def clear():
    clear_logs()
    return jsonify({"message": "Logs cleared"})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "logger", "logs_file": LOGS_FILE})


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════╗
║  Logger API  –  http://localhost:5002        ║
║  Logs file : {LOGS_FILE}
╚══════════════════════════════════════════════╝
""")
    app.run(host="0.0.0.0", port=5002, debug=False)