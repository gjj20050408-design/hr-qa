@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ==============================================
::  HR 制度智能问答系统 — 一键启动
:: ==============================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "BACKEND=%PROJECT_ROOT%\backend"
set "FRONTEND=%PROJECT_ROOT%\frontend"
set "ENV_FILE=%BACKEND%\.env"

:: 读取 .env 配置
set "ENV_NAME=hr-qa"
set "CONDA_BASE="
set "NO_CELERY=0"

if exist "%ENV_FILE%" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
        set "_v=%%b"
        if "%%a"=="CONDA_ENV_NAME"  set "ENV_NAME=!_v!"
        if "%%a"=="CONDA_BASE_PATH" set "CONDA_BASE=!_v!"
    )
)

:: 自动检测 conda 路径
if not defined CONDA_BASE (
    for /f "tokens=*" %%i in ('conda info --base 2^>nul') do set "CONDA_BASE=%%i"
)
if not defined CONDA_BASE (
    echo 致命错误：找不到 Conda！请在 backend\.env 设置 CONDA_BASE_PATH
    pause & exit /b 1
)
set "PATH=%CONDA_BASE%;%CONDA_BASE%\Scripts;%CONDA_BASE%\Library\bin;%PATH%"

if /i "%~1"=="nocelery" set "NO_CELERY=1"

:: 创建日志目录
set "LOG_DIR=%PROJECT_ROOT%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ========================================
echo   HR 制度智能问答系统 — 一键启动
echo ========================================
echo.

:: ---------- 清理旧进程 ----------
echo [*] 清理端口 8000 / 5173 上的旧进程 ...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000.*LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5173.*LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul
echo.

:: ---------- 启动后端 ----------
echo [1/3] 启动后端 API（端口 8000）...
start /b cmd /c "chcp 65001 >nul && conda.bat activate %ENV_NAME% && cd /d %BACKEND% && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > %LOG_DIR%\backend.log 2>&1"
echo   后端启动中，日志：logs\backend.log
timeout /t 3 /nobreak >nul
echo.

:: ---------- 启动前端 ----------
echo [2/3] 启动前端（端口 5173）...
start /b cmd /c "chcp 65001 >nul && cd /d %FRONTEND% && npm run dev > %LOG_DIR%\frontend.log 2>&1"
echo   前端启动中，日志：logs\frontend.log
timeout /t 2 /nobreak >nul
echo.

:: ---------- 启动 Celery ----------
if "%NO_CELERY%"=="1" (
    echo [3/3] 已跳过 Celery
) else (
    echo [3/3] 启动 Celery Worker ...
    start /b cmd /c "chcp 65001 >nul && conda.bat activate %ENV_NAME% && cd /d %BACKEND% && celery -A app.tasks.celery_app worker --loglevel=info --pool=solo > %LOG_DIR%\celery.log 2>&1"
    echo   Celery 启动中，日志：logs\celery.log
)

:: ---------- 等待就绪 ----------
echo.
echo   等待服务就绪 ...
timeout /t 4 /nobreak >nul

:: ---------- 完成 ----------
echo.
echo ========================================
echo   全部服务已在后台启动！
echo ========================================
echo   前端页面：  http://localhost:5173
echo   API 文档：  http://localhost:8000/api/docs
echo   健康检查：  http://localhost:8000/api/v1/health
echo.
echo   管理员账号：admin001 / Admin@123
echo   日志目录：  %LOG_DIR%\
echo ========================================

:: 自动打开前端页面
start "" http://localhost:5173
pause
