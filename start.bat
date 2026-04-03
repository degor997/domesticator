@echo off
chcp 65001 >nul 2>&1
echo.
echo ===================================
echo   Domesticator — Windows Setup
echo ===================================
echo.

:: --- Find any Python to bootstrap uv ---
set PY=
where python >nul 2>&1 && set PY=python && goto :has_py
where python3 >nul 2>&1 && set PY=python3 && goto :has_py
where py >nul 2>&1 && set PY=py && goto :has_py

echo [!] Python not found. Install any Python from https://python.org
echo     (just to bootstrap uv — uv will download the right version)
pause
exit /b 1

:has_py
echo [+] Bootstrap Python: %PY%

:: --- Install uv ---
echo [*] Installing uv...
%PY% -m pip install --upgrade uv --quiet 2>nul
if %errorlevel% neq 0 (
    %PY% -m pip install uv 2>nul
)
%PY% -m uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] uv install failed. Trying standalone installer...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" 2>nul
    where uv >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Could not install uv. Install manually: https://docs.astral.sh/uv/
        pause
        exit /b 1
    )
    set UV=uv
    goto :uv_ready
)
set UV=%PY% -m uv
:uv_ready
echo [+] uv ready

:: --- Let uv download Python 3.13 and install deps ---
echo.
echo [*] Installing Python 3.13 + project dependencies (uv handles everything)...
%UV% sync --all-extras --python 3.13
if %errorlevel% neq 0 (
    echo [!] Dependency installation failed.
    pause
    exit /b 1
)
echo [+] Dependencies installed

:: --- Clean old cache ---
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

:: --- Install Chromium ---
echo.
echo [*] Installing Chromium browser...
%UV% run playwright install chromium --with-deps
if %errorlevel% neq 0 (
    %UV% run playwright install chromium
    if %errorlevel% neq 0 (
        echo [!] Failed to install Chromium.
        pause
        exit /b 1
    )
)

:: --- Verify browser ---
echo [*] Verifying browser...
%UV% run python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop(); print('[+] Browser OK')"
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
%UV% run python -m http_api.serve
