#!/bin/bash

# AI Agent Security Demo - Startup Script
# Launches all necessary components

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        AI AGENT SECURITY DEMO - STARTUP SCRIPT             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function to check if a port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Function to check if Ollama is running
check_ollama() {
    curl -s http://localhost:11434/api/tags > /dev/null 2>&1
    return $?
}

echo "🔍 Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ Python 3 is installed"

# Check Ollama
if check_ollama; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Ollama is not running"
    echo "   Start it with: ollama serve"
    echo "   Or continue without AI features"
fi

# Check if ports are available
if check_port 5001; then
    echo "⚠️  Port 5001 is already in use (Security Proxy)"
fi

if check_port 5002; then
    echo "⚠️  Port 5002 is already in use (Logger API)"
fi

if check_port 8000; then
    echo "⚠️  Port 8000 is already in use (Dashboard)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STARTING SERVICES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

echo "1️⃣  Starting Security Proxy (Port 5001)..."
cd security
python3 security_proxy.py > ../logs/security_proxy.log 2>&1 &
SECURITY_PID=$!
echo "   PID: $SECURITY_PID"
cd ..

sleep 2

echo "2️⃣  Starting Logger API (Port 5002)..."
cd security
python3 logger.py > ../logs/logger.log 2>&1 &
LOGGER_PID=$!
echo "   PID: $LOGGER_PID"
cd ..

sleep 2

echo "3️⃣  Starting Dashboard Server (Port 8000)..."
cd dashboard
python3 -m http.server 8000 > ../logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "   PID: $DASHBOARD_PID"
cd ..

sleep 2

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ALL SERVICES STARTED                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Dashboard:           http://localhost:8000"
echo "🛡️  Security Proxy:      http://localhost:5001"
echo "📝 Logger API:          http://localhost:5002"
echo ""
echo "Process IDs:"
echo "  Security Proxy: $SECURITY_PID"
echo "  Logger API:     $LOGGER_PID"
echo "  Dashboard:      $DASHBOARD_PID"
echo ""
echo "To stop all services, run:"
echo "  kill $SECURITY_PID $LOGGER_PID $DASHBOARD_PID"
echo ""
echo "Or save to file:"
echo "  echo \"$SECURITY_PID $LOGGER_PID $DASHBOARD_PID\" > .demo_pids"
echo ""

# Save PIDs to file
echo "$SECURITY_PID $LOGGER_PID $DASHBOARD_PID" > .demo_pids

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Open Dashboard:"
echo "   http://localhost:8000"
echo ""
echo "2. Run Test Suite:"
echo "   ./run_tests.sh"
echo ""
echo "3. Try AI Agent:"
echo "   cd ai_agent && python3 agent_app.py"
echo ""
echo "4. View Logs:"
echo "   tail -f logs/*.log"
echo ""
