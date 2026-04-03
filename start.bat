@echo off
chcp 65001 >nul 2>&1
echo.
echo ===================================
echo   Domesticator — Windows Setup
echo ===================================
echo.

:: --- Determine Python command ---
set PY=python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    set PY=python3
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Python not found. Install Python 3.12+ from https://python.org
        echo     Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    )
)
echo [+] Python found

:: --- Check Node.js ---
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Node.js not found. Install from https://nodejs.org
    pause
    exit /b 1
)
echo [+] Node.js found

:: --- Install uv via pip ---
echo [*] Ensuring uv is installed...
%PY% -m pip install uv --quiet 2>nul
if %errorlevel% neq 0 (
    %PY% -m pip install uv
)
echo [+] uv ready

:: --- Install dependencies ---
echo.
echo [*] Installing project dependencies...
%PY% -m uv sync --all-extras
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies
    pause
    exit /b 1
)

:: --- Install Chromium ---
echo.
echo [*] Installing Chromium browser...
%PY% -m uv run playwright install chromium
if %errorlevel% neq 0 (
    echo [!] Failed to install Chromium
    pause
    exit /b 1
)

:: --- Create .env.local ---
if not exist .env.local (
    copy .env.local.example .env.local >nul
    echo [+] Created .env.local
)

:: --- Start server ---
echo.
echo ===================================
echo   Starting Domesticator...
echo   UI: http://localhost:8000
echo ===================================
echo.
set APP_ENV=development
%PY% -m uv run uvicorn http_api.run:server --reload --host 0.0.0.0 --port 8000
