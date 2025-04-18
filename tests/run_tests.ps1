# PowerShell测试运行脚本

# 颜色配置
$Green = [ConsoleColor]::Green
$Yellow = [ConsoleColor]::Yellow
$Red = [ConsoleColor]::Red

# 设置默认环境变量文件路径
$EnvFile = "./tests/.env.test"
$EnvParam = $null

# 处理自定义环境文件参数
foreach ($arg in $args) {
    if ($arg -like "--env=*") {
        $EnvFile = $arg.Substring(6)
        $EnvParam = $arg
        break
    }
}

# 加载环境变量
if (Test-Path $EnvFile) {
    Write-Host "加载环境变量: $EnvFile" -ForegroundColor $Yellow
    $EnvContent = Get-Content $EnvFile
    foreach ($line in $EnvContent) {
        if ($line -match '^([^#=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            # 移除可能的引号
            $value = $value -replace '^["'']|["'']$', ''
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
} else {
    Write-Host "警告: 环境变量文件 $EnvFile 不存在!" -ForegroundColor $Red
    Write-Host "请从 .env.example 创建 .env.test 文件" -ForegroundColor $Yellow
    exit 1
}

# 设置 PYTHONPATH
$env:PYTHONPATH = "./"

# 默认值 - 如果环境变量未设置则使用默认值
$RunAPI = $true
$RunUI = $true
$Coverage = if ($env:COVERAGE) { [System.Convert]::ToBoolean($env:COVERAGE) } else { $false }
$Parallel = if ($env:TEST_PARALLEL) { [System.Convert]::ToBoolean($env:TEST_PARALLEL) } else { $false }
$Verbose = if ($env:TEST_VERBOSE) { [System.Convert]::ToBoolean($env:TEST_VERBOSE) } else { $false }
$HTMLReport = if ($env:HTML_REPORT) { [System.Convert]::ToBoolean($env:HTML_REPORT) } else { $false }
$Random = if ($env:TEST_RANDOM) { [System.Convert]::ToBoolean($env:TEST_RANDOM) } else { $false }

# 过滤掉自定义环境文件参数
$args = $args | Where-Object { $_ -ne $EnvParam }

# 解析参数
foreach ($arg in $args) {
    switch ($arg) {
        "--api" {
            $RunAPI = $true
            $RunUI = $false
        }
        "--ui" {
            $RunAPI = $false
            $RunUI = $true
        }
        "--cov" {
            $Coverage = $true
        }
        "--parallel" {
            $Parallel = $true
        }
        "--verbose" {
            $Verbose = $true
        }
        "--html" {
            $HTMLReport = $true
        }
        "--random" {
            $Random = $true
        }
    }
}

# 输出测试运行信息
Write-Host "开始运行测试..." -ForegroundColor $Yellow
Write-Host "环境: $($env:ENVIRONMENT -eq 'test' ? $env:ENVIRONMENT : 'test')" -ForegroundColor $Green

Write-Host -NoNewline "API 测试: "
if ($RunAPI) { Write-Host "启用" -ForegroundColor $Green } else { Write-Host "禁用" -ForegroundColor $Red }

Write-Host -NoNewline "UI 测试: "
if ($RunUI) { Write-Host "启用" -ForegroundColor $Green } else { Write-Host "禁用" -ForegroundColor $Red }

Write-Host -NoNewline "覆盖率报告: "
if ($Coverage) { Write-Host "启用" -ForegroundColor $Green } else { Write-Host "禁用" -ForegroundColor $Red }

Write-Host -NoNewline "并行执行: "
if ($Parallel) { Write-Host "启用" -ForegroundColor $Green } else { Write-Host "禁用" -ForegroundColor $Red }

Write-Host -NoNewline "详细输出: "
if ($Verbose) { Write-Host "启用" -ForegroundColor $Green } else { Write-Host "禁用" -ForegroundColor $Red }

Write-Host -NoNewline "HTML报告: "
if ($HTMLReport) { Write-Host "启用" -ForegroundColor $Green } else { Write-Host "禁用" -ForegroundColor $Red }

Write-Host -NoNewline "随机顺序: "
if ($Random) { Write-Host "启用" -ForegroundColor $Green } else { Write-Host "禁用" -ForegroundColor $Red }

Write-Host ""

# 构建测试命令
$CMD = "python -m pytest"

# 设置测试范围
$TestPaths = ""
if ($RunAPI -and -not $RunUI) {
    $TestPaths = if ($env:TEST_API_PATH) { $env:TEST_API_PATH } else { "tests/api" }
}
elseif (-not $RunAPI -and $RunUI) {
    $TestPaths = if ($env:TEST_UI_PATH) { $env:TEST_UI_PATH } else { "tests/ui" }
}
else {
    $TestPaths = if ($env:TEST_DEFAULT_PATH) { $env:TEST_DEFAULT_PATH } else { "tests" }
}

# 设置参数
if ($Verbose) {
    $CMD = "$CMD -v"
}

if ($Parallel) {
    # 使用环境变量中的worker数量，如果设置为auto则不指定数量
    if ($env:TEST_PARALLEL_WORKERS -eq "auto") {
        $CMD = "$CMD -n auto"
    }
    else {
        $workers = if ($env:TEST_PARALLEL_WORKERS) { $env:TEST_PARALLEL_WORKERS } else { "auto" }
        $CMD = "$CMD -n $workers"
    }
}

if ($Random) {
    # 如果有设置随机种子，则使用它
    if ($env:TEST_RANDOM_SEED) {
        $CMD = "$CMD --random-order --random-order-seed=$($env:TEST_RANDOM_SEED)"
    }
    else {
        $CMD = "$CMD --random-order"
    }
}

if ($Coverage) {
    # 使用环境变量定义的路径
    $BackendPath = if ($env:BACKEND_COV_PATH) { $env:BACKEND_COV_PATH } else { "backend" }
    $FrontendPath = if ($env:FRONTEND_COV_PATH) { $env:FRONTEND_COV_PATH } else { "frontend" }
    $CovReportDir = if ($env:COVERAGE_REPORT_DIR) { $env:COVERAGE_REPORT_DIR } else { "tests/coverage_html_report" }
    
    $CMD = "$CMD --cov=$BackendPath --cov=$FrontendPath --cov-report=term"
    
    if ($HTMLReport) {
        $CMD = "$CMD --cov-report=html:$CovReportDir"
    }
}
elseif ($HTMLReport) {
    $HTMLPath = if ($env:HTML_REPORT_PATH) { $env:HTML_REPORT_PATH } else { "report.html" }
    $CMD = "$CMD --html=$HTMLPath"
}

# 执行测试
Write-Host "执行命令: " -ForegroundColor $Yellow -NoNewline
Write-Host "$CMD $TestPaths"
Invoke-Expression "$CMD $TestPaths"

# 输出测试结果
$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "`n测试成功通过!" -ForegroundColor $Green
    if ($Coverage -and $HTMLReport) {
        Write-Host "覆盖率报告保存在: $CovReportDir" -ForegroundColor $Green
    }
    elseif ($HTMLReport) {
        Write-Host "HTML报告保存在: $HTMLPath" -ForegroundColor $Green
    }
}
else {
    Write-Host "`n测试失败，退出代码: $exitCode" -ForegroundColor $Red
}

exit $exitCode 