@echo off
setlocal

cd /d "%~dp0"

echo ============================================================
echo   Claude Logger System - IT Quick Test
echo ============================================================
echo.
echo This will:
echo   1. Install backend dependencies
echo   2. Build dashboard-ui
echo   3. Start backend on http://127.0.0.1:8000
echo   4. Open the dashboard in the browser
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\it_test_dashboard.ps1"

echo.
echo Press any key to close this window...
pause >nul
