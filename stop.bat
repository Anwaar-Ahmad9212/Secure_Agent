@echo off
REM AI Agent Security Demo - Stop Services

echo ╔════════════════════════════════════════════════════════════╗
echo ║        STOPPING AI AGENT SECURITY DEMO                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo Stopping all Python services...

REM Kill Python processes running the demo services
taskkill /FI "WINDOWTITLE eq Security Proxy*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Logger API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Dashboard*" /F >nul 2>&1

REM Alternative: Kill by port if needed
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5001" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5002" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo ✅ All services stopped
echo.
pause