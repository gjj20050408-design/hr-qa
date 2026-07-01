@echo off
chcp 936 >nul
setlocal enabledelayedexpansion

:: ==============================================
::  HR QA System - dev launcher
::  Services run MINIMIZED (quiet in taskbar, not popping up).
::  Click a taskbar window anytime to see its live logs.
::  Usage:
::    scripts\dev.cmd            start backend + frontend + Celery
::    scripts\dev.cmd nocelery   skip Celery
:: ==============================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "BACKEND=%PROJECT_ROOT%\backend"
set "FRONTEND=%PROJECT_ROOT%\frontend"
set "ENV_FILE=%BACKEND%\.env"

set "ENV_NAME=hr-qa"
set "NO_CELERY=0"
if /i "%~1"=="nocelery" set "NO_CELERY=1"

:: infra defaults (overridable via .env)
set "MYSQL_SERVICE=MySQL"
set "DB_PORT=3306"
set "REDIS_PORT=6379"
set "REDIS_SERVER_PATH=D:\Java\Redis-x64-5.0.14.1\redis-server.exe"

:: read ports / redis path from .env
if exist "%ENV_FILE%" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
        set "_v=%%b"
        if "%%a"=="DB_PORT"           set "DB_PORT=!_v!"
        if "%%a"=="REDIS_PORT"        set "REDIS_PORT=!_v!"
        if "%%a"=="REDIS_SERVER_PATH" set "REDIS_SERVER_PATH=!_v!"
    )
)

:: ---------- locate conda ----------
set "CONDA_BASE="
for /f "tokens=*" %%i in ('conda info --base 2^>nul') do set "CONDA_BASE=%%i"
if not defined CONDA_BASE (
    echo [FATAL] Conda not found. Make sure it is installed and on PATH.
    pause & exit /b 1
)
set "CONDA_BAT=%CONDA_BASE%\Scripts\activate.bat"

echo ========================================
echo   HR QA System - dev mode
echo   Conda env: %ENV_NAME%
echo   Services start MINIMIZED in the taskbar.
echo ========================================
echo.

:: ---------- kill old processes on app ports (whole tree, retry until free) ----------
echo [*] Cleaning old processes on ports 8000 / 5173 ...
for %%P in (8000 5173) do call :kill_port %%P
echo.

:: ---------- infra: MySQL ----------
echo [infra] Checking MySQL (service %MYSQL_SERVICE%, port %DB_PORT%) ...
netstat -ano 2>nul | findstr ":%DB_PORT% .*LISTENING" >nul
if errorlevel 1 (
    echo   Port not listening, trying to start service %MYSQL_SERVICE% ...
    net start "%MYSQL_SERVICE%" >nul 2>&1
    if errorlevel 1 (
        echo   [WARN] Could not start MySQL. Run as admin or start it manually.
    ) else (
        echo   MySQL started.
    )
) else (
    echo   MySQL already running.
)

:: ---------- infra: Redis ----------
echo [infra] Checking Redis (port %REDIS_PORT%) ...
netstat -ano 2>nul | findstr ":%REDIS_PORT% .*LISTENING" >nul
if errorlevel 1 (
    if exist "%REDIS_SERVER_PATH%" (
        echo   Port not listening, starting Redis minimized ...
        start "HR-Redis" /min cmd /k "chcp 936 >nul && "%REDIS_SERVER_PATH%""
        timeout /t 2 /nobreak >nul
    ) else (
        echo   [WARN] redis-server not found: %REDIS_SERVER_PATH%
        echo          Check REDIS_SERVER_PATH in backend\.env
    )
) else (
    echo   Redis already running.
)
echo.

:: ---------- backend (minimized) ----------
echo [1/3] Starting backend API (port 8000) - minimized ...
start "HR-Backend-API" /min cmd /k "chcp 936 >nul && call "%CONDA_BAT%" %ENV_NAME% && cd /d "%BACKEND%" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: ---------- frontend (minimized) ----------
echo [2/3] Starting frontend (port 5173) - minimized ...
start "HR-Frontend" /min cmd /k "chcp 936 >nul && cd /d "%FRONTEND%" && (if not exist node_modules npm install) && npm run dev"

:: ---------- Celery (minimized) ----------
if "%NO_CELERY%"=="1" (
    echo [3/3] Skipping Celery
) else (
    echo [3/3] Starting Celery worker - minimized ...
    start "HR-Celery" /min cmd /k "chcp 936 >nul && call "%CONDA_BAT%" %ENV_NAME% && cd /d "%BACKEND%" && celery -A app.tasks.celery_app worker --loglevel=info --pool=solo"
)

echo.
echo ========================================
echo   All services launched (minimized in taskbar).
echo   Click a taskbar window to view its live logs.
echo ----------------------------------------
echo   Frontend:   http://localhost:5173
echo   API docs:   http://localhost:8000/api/docs
echo   Health:     http://localhost:8000/api/v1/health
echo   Admin acct: admin001 / Admin@123
echo ----------------------------------------
echo   To stop: close the minimized windows,
echo            or re-run this script (auto-cleans 8000/5173).
echo ========================================
echo.
echo   Waiting for services to warm up, then opening browser ...
timeout /t 6 /nobreak >nul
start "" http://localhost:5173

echo.
echo   Done. This launcher window can be closed.
pause
exit /b 0

:: ==============================================
::  :kill_port <port>
::  Kill every process tree (/T) listening on <port>,
::  retry up to 5 times until the port is actually free.
:: ==============================================
:kill_port
set "_PORT=%~1"
set "_TRIES=0"
:kp_loop
set "_FOUND=0"
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":%_PORT% .*LISTENING"') do (
    if not "%%a"=="0" (
        set "_FOUND=1"
        taskkill /PID %%a /T /F >nul 2>&1
    )
)
if "%_FOUND%"=="0" (
    echo   Port %_PORT% free.
    exit /b 0
)
set /a _TRIES+=1
if %_TRIES% GEQ 5 (
    echo   [WARN] Port %_PORT% still busy after %_TRIES% attempts.
    exit /b 0
)
timeout /t 1 /nobreak >nul
goto kp_loop
