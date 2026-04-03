@echo off
chcp 65001 >nul 2>&1
echo.
echo ===================================
echo   Domesticator — Windows Setup
echo ===================================
echo.

:: --- Determine Python command ---
set PY=
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PY=python
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PY=python3
    ) else (
        where py >nul 2>&1
        if %errorlevel% equ 0 (
            set PY=py
        )
    )
)
if "%PY%"=="" (
    echo [!] Python not found.
    echo     Install Python 3.12+ from https://python.org
    echo     IMPORTANT: Check "Add Python to PATH" during installation!
    pause
    exit /b 1
)
echo [+] Python found: %PY%

:: --- Check Node.js ---
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Node.js not found. Install from https://nodejs.org
    echo     Download LTS version and restart this script.
    pause
    exit /b 1
)
echo [+] Node.js found

:: --- Install uv ---
echo [*] Installing uv package manager...
%PY% -m pip install --upgrade uv --quiet --break-system-packages 2>nul
if %errorlevel% neq 0 (
    %PY% -m pip install --upgrade uv --quiet 2>nul
    if %errorlevel% neq 0 (
        %PY% -m pip install uv
    )
)
:: Verify uv works
%PY% -m uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] uv installation failed. Try: %PY% -m pip install uv
    pause
    exit /b 1
)
echo [+] uv ready

:: --- Clean Python cache ---
echo [*] Cleaning cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

:: --- Install project dependencies ---
echo.
echo [*] Installing project dependencies...
%PY% -m uv sync --all-extras
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies. Retrying with verbose output...
    %PY% -m uv sync --all-extras -v
    if %errorlevel% neq 0 (
        echo [!] Dependency installation failed.
        pause
        exit /b 1
    )
)
echo [+] Dependencies installed

:: --- Install Chromium with system deps ---
echo.
echo [*] Installing Chromium browser (this may take a minute)...
%PY% -m uv run playwright install chromium --with-deps
if %errorlevel% neq 0 (
    echo [!] Chromium install with --with-deps failed, trying without...
    %PY% -m uv run playwright install chromium
    if %errorlevel% neq 0 (
        echo [!] Failed to install Chromium.
        echo     Try manually: %PY% -m uv run playwright install chromium
        pause
        exit /b 1
    )
)

:: --- Verify browser works ---
echo [*] Verifying browser...
%PY% -m uv run python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop(); print('[+] Browser OK')"
if %errorlevel% neq 0 (
    echo [!] Browser verification failed. Crawl may not work.
    echo     Continuing anyway — other features will work.
)

:: --- Create .env.local ---
if not exist .env.local (
    copy .env.local.example .env.local >nul
    echo [+] Created .env.local
)

:: --- Start server ---
echo.
echo ===================================
echo   Setup complete! Starting server...
echo   UI: http://localhost:8000
echo ===================================
echo.
set APP_ENV=development
start "" http://localhost:8000
%PY% -m uv run uvicorn http_api.run:server --reload --host 0.0.0.0 --port 8000
