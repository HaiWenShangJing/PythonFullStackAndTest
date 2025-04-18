@echo off
REM 测试运行脚本 - Windows版本

REM 设置环境变量文件路径
SET ENV_FILE=tests\.env.test

REM 检查命令行参数中是否有自定义环境文件
FOR %%i IN (%*) DO (
    IF "%%i"=="--env" (
        SET ENV_FILE=%%~ni
    )
    IF "%%i:~0,6%"=="--env=" (
        SET ENV_FILE=%%i:~6%
    )
)

REM 检查环境变量文件是否存在
IF NOT EXIST %ENV_FILE% (
    ECHO 警告: 环境变量文件 %ENV_FILE% 不存在!
    ECHO 请从 .env.example 创建 .env.test 文件
    EXIT /B 1
)

REM 加载环境变量
FOR /F "tokens=*" %%a IN (%ENV_FILE%) DO (
    SET %%a
)

REM 设置环境变量
SET PYTHONPATH=./
IF NOT DEFINED ENVIRONMENT SET ENVIRONMENT=test

ECHO ==== 运行测试 ====

REM 默认参数
SET "PYTEST_ARGS="
SET "COV_ARGS="
SET "TEST_TYPE=all"

REM 处理命令行参数
:param_loop
IF "%~1"=="" GOTO :param_done
IF "%~1"=="--api" (
    SET "TEST_TYPE=api"
    SHIFT
    GOTO :param_loop
)
IF "%~1"=="--ui" (
    SET "TEST_TYPE=ui"
    SHIFT
    GOTO :param_loop
)
IF "%~1"=="--unit" (
    SET "TEST_TYPE=unit"
    SHIFT
    GOTO :param_loop
)
IF "%~1"=="--integration" (
    SET "TEST_TYPE=integration"
    SHIFT
    GOTO :param_loop
)
IF "%~1"=="--cov" (
    SET "COVERAGE=true"
    SHIFT
    GOTO :param_loop
)
IF "%~1"=="--parallel" (
    SET "TEST_PARALLEL=true"
    SHIFT
    GOTO :param_loop
)
IF "%~1"=="--verbose" (
    SET "TEST_VERBOSE=true"
    SHIFT
    GOTO :param_loop
)
IF "%~1"=="--html" (
    SET "HTML_REPORT=true"
    SHIFT
    GOTO :param_loop
)
IF "%~1"=="--random" (
    SET "TEST_RANDOM=true"
    SHIFT
    GOTO :param_loop
)
IF "%~1:~0,6%"=="--env=" (
    REM 已在前面处理
    SHIFT
    GOTO :param_loop
)
ECHO 未知参数: %~1
EXIT /B 1

:param_done

REM 环境变量默认值
IF NOT DEFINED COVERAGE SET COVERAGE=false
IF NOT DEFINED TEST_PARALLEL SET TEST_PARALLEL=false
IF NOT DEFINED TEST_VERBOSE SET TEST_VERBOSE=false
IF NOT DEFINED HTML_REPORT SET HTML_REPORT=false
IF NOT DEFINED TEST_RANDOM SET TEST_RANDOM=false

REM 输出测试配置
ECHO 环境: %ENVIRONMENT%

REM 设置测试目标
IF "%TEST_TYPE%"=="api" (
    IF DEFINED TEST_API_PATH (
        SET "TARGET=%TEST_API_PATH%"
    ) ELSE (
        SET "TARGET=tests/api"
    )
) ELSE IF "%TEST_TYPE%"=="ui" (
    IF DEFINED TEST_UI_PATH (
        SET "TARGET=%TEST_UI_PATH%"
    ) ELSE (
        SET "TARGET=tests/ui"
    )
) ELSE IF "%TEST_TYPE%"=="unit" (
    SET "TARGET=-m unit"
) ELSE IF "%TEST_TYPE%"=="integration" (
    SET "TARGET=-m integration"
) ELSE (
    IF DEFINED TEST_DEFAULT_PATH (
        SET "TARGET=%TEST_DEFAULT_PATH%"
    ) ELSE (
        SET "TARGET=tests"
    )
)

REM 构建命令选项
SET "CMD=python -m pytest"

REM 添加详细输出选项
IF "%TEST_VERBOSE%"=="true" (
    SET "CMD=%CMD% -v"
)

REM 添加并行选项
IF "%TEST_PARALLEL%"=="true" (
    IF "%TEST_PARALLEL_WORKERS%"=="auto" (
        SET "CMD=%CMD% -n auto"
    ) ELSE IF DEFINED TEST_PARALLEL_WORKERS (
        SET "CMD=%CMD% -n %TEST_PARALLEL_WORKERS%"
    ) ELSE (
        SET "CMD=%CMD% -n auto"
    )
)

REM 添加随机顺序选项
IF "%TEST_RANDOM%"=="true" (
    IF DEFINED TEST_RANDOM_SEED (
        SET "CMD=%CMD% --random-order --random-order-seed=%TEST_RANDOM_SEED%"
    ) ELSE (
        SET "CMD=%CMD% --random-order"
    )
)

REM 添加覆盖率选项
IF "%COVERAGE%"=="true" (
    IF DEFINED BACKEND_COV_PATH (
        SET "BACKEND_PATH=%BACKEND_COV_PATH%"
    ) ELSE (
        SET "BACKEND_PATH=backend"
    )
    
    IF DEFINED FRONTEND_COV_PATH (
        SET "FRONTEND_PATH=%FRONTEND_COV_PATH%"
    ) ELSE (
        SET "FRONTEND_PATH=frontend"
    )
    
    IF DEFINED COVERAGE_REPORT_DIR (
        SET "COV_REPORT_DIR=%COVERAGE_REPORT_DIR%"
    ) ELSE (
        SET "COV_REPORT_DIR=tests/coverage_html_report"
    )
    
    SET "CMD=%CMD% --cov=%BACKEND_PATH% --cov=%FRONTEND_PATH% --cov-report=term"
    
    IF "%HTML_REPORT%"=="true" (
        SET "CMD=%CMD% --cov-report=html:%COV_REPORT_DIR%"
    )
) ELSE IF "%HTML_REPORT%"=="true" (
    IF DEFINED HTML_REPORT_PATH (
        SET "HTML_PATH=%HTML_REPORT_PATH%"
    ) ELSE (
        SET "HTML_PATH=report.html"
    )
    SET "CMD=%CMD% --html=%HTML_PATH%"
)

REM 运行测试
ECHO 执行: %CMD% %TARGET%
%CMD% %TARGET%

REM 显示结果
IF %ERRORLEVEL% EQU 0 (
    ECHO ==== 测试通过 ====
    IF "%COVERAGE%"=="true" (
        IF "%HTML_REPORT%"=="true" (
            ECHO 覆盖率报告保存在: %COV_REPORT_DIR%
        )
    ) ELSE IF "%HTML_REPORT%"=="true" (
        ECHO HTML报告保存在: %HTML_PATH%
    )
    EXIT /B 0
) ELSE (
    ECHO ==== 测试失败 ====
    EXIT /B 1
) 