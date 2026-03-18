#!/bin/bash

# AI Agent Security Demo - Stop Script

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         STOPPING AI AGENT SECURITY DEMO                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ -f .demo_pids ]; then
    PIDS=$(cat .demo_pids)
    echo "Stopping processes: $PIDS"
    kill $PIDS 2>/dev/null
    echo "✅ All services stopped"
    rm .demo_pids
else
    echo "⚠️  No PID file found"
    echo "Searching for running processes..."
    
    # Find and kill processes
    pkill -f "security_proxy.py"
    pkill -f "logger.py"
    pkill -f "http.server 8000"
    
    echo "✅ Attempted to stop all related processes"
fi

echo ""
echo "Demo stopped."
