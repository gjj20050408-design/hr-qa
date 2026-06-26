<#
.SYNOPSIS
    HR 制度智能问答系统 — 启动脚本 (Windows PowerShell)

.DESCRIPTION
    启动所有服务：
    - MySQL + Redis（Docker Compose）
    - 后端 API（Uvicorn，端口 8000）
    - 前端开发服务器（Vite，端口 5173）
    - Celery 异步任务 Worker（可选）

.PARAMETER NoCelery
    跳过 Celery Worker 启动

.PARAMETER NoFrontend
    跳过前端开发服务器启动

.EXAMPLE
    .\scripts\start.ps1
    启动全部服务

.EXAMPLE
    .\scripts\start.ps1 -NoCelery
    不启动 Celery Worker
#>

param(
    [switch]$NoCelery,
    [switch]$NoFrontend
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir\.."

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  HR 制度智能问答系统 — 启动服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------- 1. 启动基础设施 ----------
Write-Host "[1/4] 启动 Docker 基础设施（MySQL + Redis） ..." -ForegroundColor Yellow

Push-Location $ProjectRoot
docker compose up -d mysql redis 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  警告：Docker Compose 启动失败，请确保 Docker Desktop 已启动。" -ForegroundColor Yellow
} else {
    Write-Host "  MySQL + Redis 已启动。" -ForegroundColor Green
}

# 等待 MySQL 就绪
Write-Host "  等待 MySQL 就绪 ..." -ForegroundColor Yellow
for ($i = 1; $i -le 30; $i++) {
    $result = docker exec hr-qa-mysql mysqladmin ping -h localhost -uroot -ppassword 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  MySQL 已就绪。" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 2
}
Pop-Location

# ---------- 2. 启动后端 ----------
Write-Host ""
Write-Host "[2/4] 启动后端 API 服务（端口 8000） ..." -ForegroundColor Yellow

$activateScript = Join-Path (conda info --base) "Scripts\activate.bat"
$backendCmd = @"
call "$activateScript" hr-qa
cd /d "$ProjectRoot\backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@

$backendProcess = Start-Process cmd -ArgumentList "/c $backendCmd" -PassThru -WindowStyle Minimized
Write-Host "  后端已启动（PID: $($backendProcess.Id)），API 文档：http://localhost:8000/api/docs" -ForegroundColor Green

# ---------- 3. 启动 Celery（可选） ----------
if (-not $NoCelery) {
    Write-Host ""
    Write-Host "[3/4] 启动 Celery Worker ..." -ForegroundColor Yellow

    $celeryCmd = @"
call "$activateScript" hr-qa
cd /d "$ProjectRoot\backend"
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
"@

    $celeryProcess = Start-Process cmd -ArgumentList "/c $celeryCmd" -PassThru -WindowStyle Minimized
    Write-Host "  Celery Worker 已启动（PID: $($celeryProcess.Id)）。" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[3/4] 已跳过 Celery Worker（--NoCelery）。" -ForegroundColor Yellow
}

# ---------- 4. 启动前端 ----------
if (-not $NoFrontend) {
    Write-Host ""
    Write-Host "[4/4] 启动前端开发服务器（端口 5173） ..." -ForegroundColor Yellow

    $frontendCmd = @"
cd /d "$ProjectRoot\frontend"
npm run dev
"@

    $frontendProcess = Start-Process cmd -ArgumentList "/c $frontendCmd" -PassThru -WindowStyle Minimized
    Write-Host "  前端已启动（PID: $($frontendProcess.Id)），页面地址：http://localhost:5173" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[4/4] 已跳过前端（--NoFrontend）。" -ForegroundColor Yellow
}

# ---------- 完成 ----------
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  所有服务已启动！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  访问地址：" -ForegroundColor White
Write-Host "    前端页面：  http://localhost:5173" -ForegroundColor Cyan
Write-Host "    API 文档：  http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "    健康检查：  http://localhost:8000/api/v1/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "  预置管理员账号：admin001 / Admin@123" -ForegroundColor White
Write-Host ""
Write-Host "  提示：在各自的终端窗口中可以查看运行日志。" -ForegroundColor Yellow
Write-Host "       关闭本窗口不会停止服务，请手动关闭各终端窗口或执行：docker compose down" -ForegroundColor Yellow
