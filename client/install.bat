@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ====================================================
echo   Claude Prompt Logger Installer for Windows
echo ====================================================
echo.

REM Kiem tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python chua duoc cai dat hoac chua duoc them vao PATH.
    echo Vui long cai dat Python va thu lai.
    pause
    exit /b 1
)

REM Hoi nhap Email
set EMAIL=
set /p EMAIL="Nhap email cua ban (An Enter de dung mac dinh tu file JSON): "

echo.
echo [1/2] Dang tien hanh cai dat hook...
if "!EMAIL!"=="" (
    python install_hook.py
) else (
    python install_hook.py --employee-email "!EMAIL!"
)

if %errorlevel% neq 0 (
    echo [ERROR] Cai dat that bai!
    pause
    exit /b 1
)

echo.
echo [2/2] Dang chay kiem tra ket noi toi Backend (Test)...
python install_hook.py --test

if %errorlevel% neq 0 (
    echo [WARNING] Kiem tra ket noi that bai! Vui long kiem tra lai ngrok hoac server backend.
) else (
    echo [SUCCESS] Kiem tra ket noi thanh cong! He thong da san sang.
)

echo.
echo ====================================================
pause
