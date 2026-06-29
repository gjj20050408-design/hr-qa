# ============================================================
# HR制度智能问答系统 — 本地一键启动脚本 (Windows PowerShell)
# ============================================================
# 前置条件：
#   1. MySQL 8.0 已安装并运行（默认端口 3306）
#   2. Redis 7 已安装并运行（默认端口 6379）
#   3. Python 3.11+ 已安装
#   4. Node.js 18+ 已安装
# ============================================================

$ErrorActionPreference = "Stop"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  HR制度智能问答系统 - 本地开发启动" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. 初始化数据库 ──
Write-Host "[1/4] 初始化 MySQL 数据库..." -ForegroundColor Yellow

$envFile = Join-Path $ROOT "backend\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$' -and -not $_.TrimStart().StartsWith('#')) {
            $key = $Matches[1].Trim()
            $val = $Matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $val, "Process")
        }
    }
}

$DB_HOST = $env:DB_HOST ? $env:DB_HOST : "localhost"
$DB_PORT = $env:DB_PORT ? $env:DB_PORT : "3306"
$DB_USER = $env:DB_USER ? $env:DB_USER : "root"
$DB_PASSWORD = $env:DB_PASSWORD ? $env:DB_PASSWORD : "password"
$DB_NAME = $env:DB_NAME ? $env:DB_NAME : "hr_policy_qa"

Write-Host "  连接: $DB_USER@${DB_HOST}:$DB_PORT" -ForegroundColor Gray

# 创建数据库（如不存在）
$sqlCmd = "CREATE DATABASE IF NOT EXISTS $DB_NAME DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
$escapedSql = $sqlCmd -replace '"', '""'
$result = & cmd /c "echo $escapedSql | mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  警告：无法自动创建数据库（可能已存在或 MySQL 未运行）" -ForegroundColor DarkYellow
    Write-Host "  $result" -ForegroundColor DarkGray
} else {
    Write-Host "  数据库 $DB_NAME 已就绪" -ForegroundColor Green
}

# 执行初始化SQL（仅插入种子数据，建表由后端自动完成）
$initSql = Join-Path $ROOT "backend\init_db.sql"
if (Test-Path $initSql) {
    Write-Host "  执行种子数据初始化..." -ForegroundColor Gray
    $result = & cmd /c "mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME < `"$initSql`" 2>&1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  种子数据可能已存在，跳过" -ForegroundColor Gray
    } else {
        Write-Host "  种子数据初始化完成" -ForegroundColor Green
    }
}

# ── 2. 安装后端依赖 ──
Write-Host ""
Write-Host "[2/4] 安装后端 Python 依赖..." -ForegroundColor Yellow

$backendDir = Join-Path $ROOT "backend"
Set-Location $backendDir
pip install -r requirements.txt -q
Write-Host "  后端依赖已就绪" -ForegroundColor Green

# ── 3. 安装前端依赖 ──
Write-Host ""
Write-Host "[3/4] 安装前端 Node.js 依赖..." -ForegroundColor Yellow

$frontendDir = Join-Path $ROOT "frontend"
Set-Location $frontendDir
npm install --silent 2>$null
Write-Host "  前端依赖已就绪" -ForegroundColor Green

# ── 4. 启动服务 ──
Write-Host ""
Write-Host "[4/4] 启动后端(8000) + 前端(5173)..." -ForegroundColor Yellow
Write-Host ""

# 启动后端
$backendJob = Start-Job -Name "hr-backend" -ScriptBlock {
    param($dir)
    Set-Location $dir
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} -ArgumentList $backendDir

# 启动前端
$frontendJob = Start-Job -Name "hr-frontend" -ScriptBlock {
    param($dir)
    Set-Location $dir
    npx vite --host 0.0.0.0 --port 5173
} -ArgumentList $frontendDir

# 等待启动
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  系统启动完成！" -ForegroundColor Green
Write-Host "  " -ForegroundColor Green
Write-Host "  前端页面： http://localhost:5173" -ForegroundColor White
Write-Host "  API 文档： http://localhost:8000/api/docs" -ForegroundColor White
Write-Host "  " -ForegroundColor Green
Write-Host "  默认管理员： admin001 / Admin@123" -ForegroundColor Gray
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止所有服务..." -ForegroundColor DarkYellow
Write-Host ""

# 等待用户中断
try {
    while ($true) {
        # 检查后端是否异常退出
        if ($backendJob.State -eq "Failed") {
            Write-Host "后端服务异常退出：" -ForegroundColor Red
            Receive-Job $backendJob
            break
        }
        if ($frontendJob.State -eq "Failed") {
            Write-Host "前端服务异常退出：" -ForegroundColor Red
            Receive-Job $frontendJob
            break
        }
        Start-Sleep -Seconds 2
    }
}
finally {
    Write-Host ""
    Write-Host "正在停止服务..." -ForegroundColor Yellow
    Stop-Job -Name "hr-backend" -ErrorAction SilentlyContinue
    Stop-Job -Name "hr-frontend" -ErrorAction SilentlyContinue
    Remove-Job -Name "hr-backend" -ErrorAction SilentlyContinue
    Remove-Job -Name "hr-frontend" -ErrorAction SilentlyContinue
    Write-Host "所有服务已停止" -ForegroundColor Green
}
