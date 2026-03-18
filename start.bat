@echo off
set PYTHONIOENCODING=utf-8
REM AI Agent Security Demo - Windows Launcher
REM This script starts all necessary services for the demo

echo ╔════════════════════════════════════════════════════════════╗
echo ║     AI AGENT SECURITY DEMO - WINDOWS LAUNCHER              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python is installed

REM Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama is not running
    echo Please start Ollama before running this script
    echo You can start it with: ollama serve
    echo.
    echo Continue anyway? (Y/N)
    set /p continue=
    if /i not "%continue%"=="Y" exit /b 1
)
echo ✅ Ollama is running

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo STARTING SERVICES
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Create logs directory
if not exist "logs" mkdir logs

echo 1️⃣  Starting Security Proxy (Port 5001)...
start "Security Proxy" /MIN cmd /c "cd security && python security_proxy.py > ..\logs\security_proxy.log 2>&1"
timeout /t 2 /nobreak >nul

echo 2️⃣  Starting Logger API (Port 5002)...
start "Logger API" /MIN cmd /c "cd security && python logger.py > ..\logs\logger.log 2>&1"
timeout /t 2 /nobreak >nul

echo 3️⃣  Starting Dashboard Server (Port 8000)...
start "Dashboard" /MIN cmd /c "cd dashboard && python -m http.server 8000 > ..\logs\dashboard.log 2>&1"
timeout /t 2 /nobreak >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                  ALL SERVICES STARTED                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📊 Dashboard:           http://localhost:8000
echo 🛡️  Security Proxy:      http://localhost:5001
echo 📝 Logger API:          http://localhost:5002
echo.
echo Opening dashboard in your default browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo DEMO IS RUNNING
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo The services are running in minimized windows.
echo.
echo To submit prompts:
echo   - Use the Input Page: http://localhost:8000/input.html
echo   - Or use the dashboard to monitor activity
echo.
echo Press Ctrl+C to stop all services...
echo.

REM Keep this window open until user presses Ctrl+C
:loop
timeout /t 1 /nobreak >nul
goto loop