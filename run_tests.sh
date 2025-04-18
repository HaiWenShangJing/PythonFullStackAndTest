#!/bin/bash
# 测试运行脚本

# 设置环境变量
export PYTHONPATH=./
export ENVIRONMENT=test

# 加载测试环境变量
set -a
source ./tests/.env.test
set +a

echo "==== 运行测试 ===="

# 默认参数
PYTEST_ARGS=""
COV_ARGS=""
TEST_TYPE="all"

# 处理命令行参数
while [ "$#" -gt 0 ]; do
    case "$1" in
        --api) TEST_TYPE="api"; shift 1;;
        --ui) TEST_TYPE="ui"; shift 1;;
        --unit) TEST_TYPE="unit"; shift 1;;
        --integration) TEST_TYPE="integration"; shift 1;;
        --cov) COV_ARGS="--cov=backend --cov=frontend --cov-report=term --cov-report=html"; shift 1;;
        --parallel) PYTEST_ARGS="$PYTEST_ARGS -xvs -n auto"; shift 1;;
        --verbose) PYTEST_ARGS="$PYTEST_ARGS -vvs"; shift 1;;
        *) echo "未知参数: $1"; exit 1;;
    esac
done

# 设置测试目标
case "$TEST_TYPE" in
    api) TARGET="tests/api";;
    ui) TARGET="tests/ui";;
    unit) TARGET="-m unit";;
    integration) TARGET="-m integration";;
    all) TARGET="tests";;
esac

# 运行测试
echo "执行: pytest $TARGET $PYTEST_ARGS $COV_ARGS"
python -m pytest $TARGET $PYTEST_ARGS $COV_ARGS

# 显示结果
if [ $? -eq 0 ]; then
    echo "==== 测试通过 ===="
    if [[ "$COV_ARGS" != "" ]]; then
        echo "覆盖率报告保存在: tests/coverage_html_report"
    fi
    exit 0
else
    echo "==== 测试失败 ===="
    exit 1
fi 