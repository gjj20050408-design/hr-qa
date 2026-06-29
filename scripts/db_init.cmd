@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ==============================================
::  HR 制度智能问答系统 — 数据库初始化脚本
::  功能: 从 backend\init_db.sql 初始化 MySQL 数据库
::  用法: 双击运行，或在命令行执行 scripts\db_init.cmd
:: ==============================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "ENV_FILE=%PROJECT_ROOT%\backend\.env"

:: ---- 默认值 ----
set "DB_HOST=localhost"
set "DB_PORT=3306"
set "DB_USER=root"
set "DB_PASSWORD=password"
set "DB_NAME=hr_policy_qa"

:: ---- 从 .env 读取数据库配置 ----
if exist "%ENV_FILE%" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
        if "%%a"=="DB_HOST"     set "DB_HOST=%%b"
        if "%%a"=="DB_PORT"     set "DB_PORT=%%b"
        if "%%a"=="DB_USER"     set "DB_USER=%%b"
        if "%%a"=="DB_PASSWORD" set "DB_PASSWORD=%%b"
        if "%%a"=="DB_NAME"     set "DB_NAME=%%b"
    )
)

:: ---- 提示 ----
echo ========================================
echo   HR 制度智能问答系统 — 数据库初始化
echo ========================================
echo.
echo   连接信息:
echo     主机: %DB_HOST%:%DB_PORT%
echo     用户: %DB_USER%
echo     数据库: %DB_NAME%
echo.

:: ---- 检查 MySQL 客户端 ----
where mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 找不到 mysql 命令行工具，请安装 MySQL 并将 bin 目录加入 PATH。
    pause
    exit /b 1
)

:: ---- 检查 MySQL 连接 ----
echo [1] 检测 MySQL 连接 ...
mysqladmin ping -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASSWORD% --silent >nul 2>&1
if !errorlevel! neq 0 (
    echo [警告] MySQL 无响应，请确认 MySQL 服务已启动。
    echo         若需修改连接信息，请编辑 backend\.env
    echo.
    pause
    exit /b 1
)
echo    MySQL 连接正常。

:: ---- 创建数据库 ----
echo [2] 创建数据库 %DB_NAME% ...
mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASSWORD% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
if !errorlevel! neq 0 (
    echo [错误] 数据库创建失败！
    pause
    exit /b 1
)
echo    数据库已就绪。

:: ---- 导入 init_db.sql ----
set "SQL_FILE=%PROJECT_ROOT%\backend\init_db.sql"
echo [3] 导入 %SQL_FILE% ...
mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASSWORD% --default-character-set=utf8mb4 %DB_NAME% < "%SQL_FILE%" 2>nul
if !errorlevel! equ 0 (
    echo    导入成功！
) else (
    echo [错误] SQL 导入失败，请检查 init_db.sql 文件。
    pause
    exit /b 1
)

echo.
echo ========================================
echo   数据库初始化完成！
echo ========================================
echo.
echo   已创建表和数据:
echo     - 14 张表 (DDL)
echo     - 预置部门 (5 个)
echo     - 预置分类 (document + faq)
echo     - 预置管理员账号 (admin001 / Admin@123)
echo     - 员工数据敏感度配置 (16 条)
echo.
pause
