#!/usr/bin/env python3
"""
Security Event Logger
Logs all security events and provides API for dashboard.
"""

import json
import os
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

LOGS_FILE = "logs.json"


def init_logs_file():
    """Initialize logs file if it doesn't exist."""
    if not os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'w') as f:
            json.dump([], f)


def log_event(source, prompt, action, reason="", tool="", severity="medium", metadata=None):
    """
    Log a security event.
    
    Args:
        source: Origin of the request (ai_agent, n8n, api)
        prompt: The user prompt or input
        action: allowed or blocked
        reason: Why it was allowed/blocked
        tool: Which tool was attempted
        severity: low, medium, high, critical
        metadata: Additional information
    """
    init_logs_file()
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "prompt": prompt[:500],  # Truncate long prompts
        "action": action,
        "reason": reason,
        "tool": tool,
        "severity": severity,
        "metadata": metadata or {}
    }
    
    # Read existing logs
    with open(LOGS_FILE, 'r') as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    
    # Add new event
    logs.append(event)
    
    # Keep only last 1000 events
    logs = logs[-1000:]
    
    # Write back
    with open(LOGS_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    # Print to console
    print(f"\n[{event['timestamp']}] {event['action'].upper()}: {event['source']}")
    print(f"  Prompt: {event['prompt'][:100]}...")
    print(f"  Reason: {event['reason']}")
    print(f"  Severity: {event['severity']}\n")
    
    return event


@app.route('/logs', methods=['GET'])
def get_logs():
    """Get all logs."""
    init_logs_file()
    
    try:
        with open(LOGS_FILE, 'r') as f:
            logs = json.load(f)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/logs/recent', methods=['GET'])
def get_recent_logs():
    """Get recent logs (last 50)."""
    init_logs_file()
    
    try:
        with open(LOGS_FILE, 'r') as f:
            logs = json.load(f)
        return jsonify(logs[-50:])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Get only blocked events (alerts)."""
    init_logs_file()
    
    try:
        with open(LOGS_FILE, 'r') as f:
            logs = json.load(f)
        
        alerts = [log for log in logs if log['action'] == 'blocked']
        return jsonify(alerts[-50:])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics."""
    init_logs_file()
    
    try:
        with open(LOGS_FILE, 'r') as f:
            logs = json.load(f)
        
        total = len(logs)
        blocked = len([log for log in logs if log['action'] == 'blocked'])
        allowed = len([log for log in logs if log['action'] == 'allowed'])
        
        # Count by severity
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for log in logs:
            severity = log.get('severity', 'medium')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Count by source
        source_counts = {}
        for log in logs:
            source = log.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        stats = {
            "total_requests": total,
            "blocked": blocked,
            "allowed": allowed,
            "block_rate": round(blocked / total * 100, 2) if total > 0 else 0,
            "severity_counts": severity_counts,
            "source_counts": source_counts
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/clear', methods=['POST'])
def clear_logs():
    """Clear all logs."""
    with open(LOGS_FILE, 'w') as f:
        json.dump([], f)
    
    return jsonify({"message": "Logs cleared successfully"})


if __name__ == "__main__":
    init_logs_file()
    print("""
╔════════════════════════════════════════════════════════════╗
║         Security Logger API Server                         ║
║                                                            ║
║  Running on: http://localhost:5002                         ║
║                                                            ║
║  Endpoints:                                                ║
║  - GET  /logs         : All logs                           ║
║  - GET  /logs/recent  : Recent logs                        ║
║  - GET  /alerts       : Blocked events only                ║
║  - GET  /stats        : Statistics                         ║
║  - POST /clear        : Clear logs                         ║
╚════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5002, debug=True)
