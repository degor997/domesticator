@echo off
chcp 65001 >nul 2>&1
echo.
echo ===================================
echo   Domesticator — Windows Setup
echo ===================================
echo.

:: --- Try to find Python 3.12 or 3.13 first (py launcher) ---
set PY=

:: Try py launcher with specific versions first
where py >nul 2>&1
if %errorlevel% equ 0 (
    py -3.13 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PY=py -3.13
        goto :py_found
    )
    py -3.12 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PY=py -3.12
        goto :py_found
    )
)

:: Try python3/python and check version
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PY=python
    goto :check_version
)
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PY=python3
    goto :check_version
)

echo [!] Python not found.
echo     Install Python 3.12 or 3.13 from https://python.org
echo     IMPORTANT: Check "Add Python to PATH" during installation!
pause
exit /b 1

:check_version
:: Check if Python version is 3.12 or 3.13 (not 3.14+)
%PY% -c "import sys; v=sys.version_info; exit(0 if v.minor in (12,13) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Found Python, but it's not 3.12 or 3.13.
    echo     Playwright does NOT work with Python 3.14+.
    echo.
    echo     Please install Python 3.12 or 3.13:
    echo       https://www.python.org/downloads/release/python-3131/
    echo.
    echo     If you have multiple Python versions, use the py launcher:
    echo       py -3.13 --version
    echo.
    :: Check if py launcher can find 3.12 or 3.13
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        py -3.13 --version >nul 2>&1
        if %errorlevel% equ 0 (
            set PY=py -3.13
            echo     Found Python 3.13 via py launcher, using it!
            goto :py_found
        )
        py -3.12 --version >nul 2>&1
        if %errorlevel% equ 0 (
            set PY=py -3.12
            echo     Found Python 3.12 via py launcher, using it!
            goto :py_found
        )
    )
    pause
    exit /b 1
)

:py_found
echo [+] Python found: %PY%
for /f "tokens=*" %%i in ('%PY% --version 2^>^&1') do echo     %%i

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
%PY% -m uv sync --all-extras --python 3.12 2>nul || %PY% -m uv sync --all-extras --python 3.13 2>nul || %PY% -m uv sync --all-extras
if %errorlevel% neq 0 (
    echo [!] Dependency installation failed.
    pause
    exit /b 1
)
echo [+] Dependencies installed

:: --- Install Chromium ---
echo.
echo [*] Installing Chromium browser (this may take a minute)...
%PY% -m uv run playwright install chromium --with-deps
if %errorlevel% neq 0 (
    %PY% -m uv run playwright install chromium
    if %errorlevel% neq 0 (
        echo [!] Failed to install Chromium.
        pause
        exit /b 1
    )
)

:: --- Verify browser works ---
echo [*] Verifying browser...
%PY% -m uv run python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop(); print('[+] Browser OK')"
if %errorlevel% neq 0 (
    echo [!] Browser verification failed. Crawl may not work.
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
