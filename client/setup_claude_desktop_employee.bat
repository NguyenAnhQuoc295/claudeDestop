@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo   Claude Desktop Prompt Logger - Employee Setup
echo ============================================================
echo.
echo This installer only asks for employee email.
echo Other settings are read from:
echo   %~dp0install_defaults.json
echo.

if not exist "install_defaults.json" (
    echo [ERROR] Missing install_defaults.json
    echo Create it from install_defaults.example.json, then update api_url/api_key.
    echo.
    pause
    exit /b 1
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not available in PATH.
    echo Please install Python 3.11+ and tick "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

echo [Config]
python -c "import json; c=json.load(open('install_defaults.json', encoding='utf-8')); print('  api_url=' + str(c.get('api_url',''))); print('  api_key=' + ('***' if c.get('api_key') else '')); print('  log_dir=' + str(c.get('log_dir','default')))"
if %errorlevel% neq 0 (
    echo [ERROR] install_defaults.json is not valid JSON.
    echo.
    pause
    exit /b 1
)

python -c "import json, sys; c=json.load(open('install_defaults.json', encoding='utf-8')); u=str(c.get('api_url','')); sys.exit(1 if ('SERVER_IP_OR_DOMAIN' in u or not u.strip()) else 0)"
if %errorlevel% neq 0 (
    echo [ERROR] install_defaults.json api_url is not configured.
    echo Please replace SERVER_IP_OR_DOMAIN with your real server IP/domain.
    echo Example:
    echo   http://192.168.1.50:8000/api/claude/prompt-log
    echo.
    pause
    exit /b 1
)

echo.
set EMPLOYEE_EMAIL=
set /p EMPLOYEE_EMAIL="Enter employee email: "

if "!EMPLOYEE_EMAIL!"=="" (
    echo [ERROR] Employee email is required.
    echo.
    pause
    exit /b 1
)

echo.
echo [1/3] Installing Claude Desktop MCP logger...
python install_claude_desktop_mcp.py --employee-email "!EMPLOYEE_EMAIL!"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Claude Desktop MCP logger installation failed.
    pause
    exit /b 1
)

echo.
echo [2/3] Testing connection to backend server...
python prompt_logger_common.py --test
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Backend test failed.
    echo The local MCP setup was written, but this computer cannot reach the server yet.
    echo Check install_defaults.json api_url, company network/VPN, and server firewall.
) else (
    echo.
    echo [SUCCESS] Backend connection test passed.
)

echo.
echo [3/3] Next step:
echo   1. Close Claude Desktop completely.
echo   2. Open Claude Desktop again.
echo   3. Go to Settings ^> Developer ^> Local MCP servers.
echo   4. Check that company-prompt-logger is running.
echo.
echo Local prompt log folder:
echo   %USERPROFILE%\CompanyClaudeLogs
echo.
echo ============================================================
pause
