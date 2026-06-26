@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ==============================================
::  HR 制度智能问答系统 — 初始化脚本
:: ==============================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "ENV_FILE=%PROJECT_ROOT%\backend\.env"

:: 读取 .env 配置
set "ENV_NAME=hr-qa"
set "REDIS_SERVER_PATH="
set "CONDA_BASE="

if exist "%ENV_FILE%" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
        set "_v=%%b"
        if "%%a"=="CONDA_ENV_NAME"    set "ENV_NAME=!_v!"
        if "%%a"=="CONDA_BASE_PATH"   set "CONDA_BASE=!_v!"
        if "%%a"=="REDIS_SERVER_PATH" set "REDIS_SERVER_PATH=!_v!"
    )
)

:: 备选：自动检测 conda 路径
if not defined CONDA_BASE (
    for /f "tokens=*" %%i in ('conda info --base 2^>nul') do set "CONDA_BASE=%%i"
)
if not defined CONDA_BASE (
    echo 致命错误：无法确定 Conda 路径！请在 backend\.env 中设置 CONDA_BASE_PATH
    pause & exit /b 1
)

:: 把 conda 加入 PATH
set "PATH=%CONDA_BASE%;%CONDA_BASE%\Scripts;%CONDA_BASE%\Library\bin;%PATH%"

echo ========================================
echo   HR 制度智能问答系统 — 项目初始化
echo ========================================
echo.

:: ---------- 1. 检查 Conda ----------
echo [1/6] 检查 Conda ...
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：conda 不可用，请检查 CONDA_BASE_PATH
    pause & exit /b 1
)
echo   Conda 已就绪。

:: ---------- 2. 创建环境 ----------
echo [2/6] 创建环境 "%ENV_NAME%" ...
conda env list | findstr /C:"%ENV_NAME%" >nul 2>&1
if !errorlevel! equ 0 (
    echo   环境已存在，跳过。
) else (
    conda create -n %ENV_NAME% python=3.11 -y
    conda env list | findstr /C:"%ENV_NAME%" >nul 2>&1
    if !errorlevel! neq 0 (
        echo   创建失败！
        pause & exit /b 1
    )
    echo   环境创建成功。
)

:: ---------- 3. 安装 Python 依赖 ----------
echo [3/6] 安装 Python 依赖 ...
call conda.bat activate %ENV_NAME%
pip install -r "%PROJECT_ROOT%\backend\requirements.txt"
if !errorlevel! neq 0 (
    echo   依赖安装失败！
    pause & exit /b 1
)
echo   Python 依赖就绪。

:: ---------- 4. 检查本地服务 ----------
echo [4/6] 检查 MySQL / Redis ...
mysqladmin ping -h localhost -uroot -ppassword >nul 2>&1 && echo   MySQL  就绪 || echo   警告：MySQL 未响应
redis-cli ping >nul 2>&1 && echo   Redis  就绪 || echo   警告：Redis 未响应

:: ---------- 5. 初始化数据库 ----------
echo [5/6] 初始化数据库 ...
mysql -uroot -ppassword -e "CREATE DATABASE IF NOT EXISTS hr_policy_qa DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
mysql -uroot -ppassword --default-character-set=utf8mb4 hr_policy_qa < "%PROJECT_ROOT%\backend\init_db.sql" 2>nul
if !errorlevel! equ 0 (
    echo   数据库初始化完成。
) else (
    echo   警告：数据库初始化失败，请检查 MySQL。
)

:: ---------- 6. 安装前端依赖 ----------
echo [6/6] 安装前端依赖 ...
cd /d "%PROJECT_ROOT%\frontend"
call npm install
if !errorlevel! equ 0 (
    echo   前端依赖就绪。
) else (
    echo   前端依赖安装失败！
)

echo.
echo ========================================
echo   初始化完成！运行 scripts\start.cmd 启动
echo ========================================
pause
