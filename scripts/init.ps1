<#
.SYNOPSIS
    HR 制度智能问答系统 — 项目初始化脚本 (Windows PowerShell)

.DESCRIPTION
    自动完成以下步骤：
    1. 检查 Conda 是否安装
    2. 创建 Conda 环境 hr-qa（Python 3.11）
    3. 安装 Python 依赖
    4. 启动 Docker Compose 基础设施（MySQL + Redis）
    5. 初始化数据库（建库 + 建表 + 预置数据）
    6. 安装前端依赖
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir\.."

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  HR 制度智能问答系统 — 项目初始化" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------- 1. 检查 Conda ----------
Write-Host "[1/6] 检查 Conda ..." -ForegroundColor Yellow

$condaPath = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaPath) {
    Write-Host "错误：未检测到 Conda，请先安装 Miniconda 或 Anaconda。" -ForegroundColor Red
    Write-Host "下载地址：https://docs.conda.io/en/latest/miniconda.html" -ForegroundColor Red
    exit 1
}
Write-Host "  Conda 已就绪：$($condaPath.Source)" -ForegroundColor Green

# ---------- 2. 创建 Conda 环境 ----------
$envName = "hr-qa"
Write-Host ""
Write-Host "[2/6] 创建 Conda 环境 '$envName' ..." -ForegroundColor Yellow

$envExists = conda env list | Select-String "^\s*$envName\s"
if ($envExists) {
    Write-Host "  环境 '$envName' 已存在，跳过创建。" -ForegroundColor Green
} else {
    conda create -n $envName python=3.11 -y
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  创建环境失败，请检查网络连接。" -ForegroundColor Red
        exit 1
    }
    Write-Host "  环境 '$envName' 创建成功。" -ForegroundColor Green
}

# ---------- 3. 安装 Python 依赖 ----------
Write-Host ""
Write-Host "[3/6] 安装 Python 依赖 ..." -ForegroundColor Yellow

$activateScript = Join-Path (conda info --base) "Scripts\activate.bat"
$pipInstall = @"
call "$activateScript" $envName
pip install -r "$ProjectRoot\backend\requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple
"@
$pipInstall | cmd /c

if ($LASTEXITCODE -ne 0) {
    Write-Host "  依赖安装失败，正在尝试使用默认源 ..." -ForegroundColor Yellow
    $pipInstallFallback = @"
call "$activateScript" $envName
pip install -r "$ProjectRoot\backend\requirements.txt"
"@
    $pipInstallFallback | cmd /c
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  依赖安装失败！" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  Python 依赖安装完成。" -ForegroundColor Green

# ---------- 4. 启动基础设施 ----------
Write-Host ""
Write-Host "[4/6] 启动 Docker 基础设施（MySQL + Redis） ..." -ForegroundColor Yellow

Push-Location $ProjectRoot
docker compose up -d mysql redis 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  警告：Docker Compose 启动失败，请确保 Docker Desktop 已启动。" -ForegroundColor Yellow
    Write-Host "  你也可以手动启动 MySQL 和 Redis 服务后继续。" -ForegroundColor Yellow
} else {
    Write-Host "  MySQL + Redis 容器已启动。" -ForegroundColor Green
}
Pop-Location

# ---------- 5. 初始化数据库 ----------
Write-Host ""
Write-Host "[5/6] 初始化数据库 ..." -ForegroundColor Yellow

$mysqlReady = $false
$maxRetries = 30
for ($i = 1; $i -le $maxRetries; $i++) {
    $result = docker exec hr-qa-mysql mysqladmin ping -h localhost -uroot -ppassword 2>&1
    if ($LASTEXITCODE -eq 0) {
        $mysqlReady = $true
        break
    }
    Write-Host "  等待 MySQL 就绪 ... ($i/$maxRetries)"
    Start-Sleep -Seconds 2
}

if ($mysqlReady) {
    Write-Host "  MySQL 已就绪，正在执行初始化 SQL ..." -ForegroundColor Green
    Get-Content "$ProjectRoot\backend\init_db.sql" | docker exec -i hr-qa-mysql mysql -uroot -ppassword
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  数据库初始化完成。" -ForegroundColor Green
    } else {
        Write-Host "  警告：数据库初始化可能失败，请手动执行 backend/init_db.sql。" -ForegroundColor Yellow
    }
} else {
    Write-Host "  错误：MySQL 未能启动，请检查 Docker 状态后手动执行：" -ForegroundColor Red
    Write-Host "    docker exec -i hr-qa-mysql mysql -uroot -ppassword < backend\init_db.sql" -ForegroundColor Red
}

# ---------- 6. 安装前端依赖 ----------
Write-Host ""
Write-Host "[6/6] 安装前端依赖 ..." -ForegroundColor Yellow

Push-Location "$ProjectRoot\frontend"
npm install 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  前端依赖安装完成。" -ForegroundColor Green
} else {
    Write-Host "  前端依赖安装失败，请手动执行：cd frontend && npm install" -ForegroundColor Red
}
Pop-Location

# ---------- 完成 ----------
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  初始化完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  下一步：执行启动脚本" -ForegroundColor White
Write-Host "    .\scripts\start.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "  或手动启动：" -ForegroundColor White
Write-Host "    conda activate hr-qa" -ForegroundColor Cyan
Write-Host "    cd backend && uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host "    cd frontend && npm run dev" -ForegroundColor Cyan
