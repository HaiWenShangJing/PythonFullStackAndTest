#!/bin/bash

# 颜色配置
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 设置默认环境变量文件路径
ENV_FILE="./tests/.env.test"

# 加载环境变量
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}加载环境变量: $ENV_FILE${NC}"
    set -a
    source "$ENV_FILE"
    set +a
else
    echo -e "${RED}警告: 环境变量文件 $ENV_FILE 不存在!${NC}"
    echo -e "${YELLOW}请从 .env.example 创建 .env.test 文件${NC}"
    exit 1
fi

# 设置 PYTHONPATH
export PYTHONPATH=./

# 默认值 - 如果环境变量未设置则使用默认值
RUN_API=true
RUN_UI=true
COVERAGE=${COVERAGE:-false}
PARALLEL=${TEST_PARALLEL:-false}
VERBOSE=${TEST_VERBOSE:-false}
HTML_REPORT=${HTML_REPORT:-false}
RANDOM=${TEST_RANDOM:-false}

# 解析参数
for arg in "$@"
do
    case $arg in
        --api)
        RUN_API=true
        RUN_UI=false
        shift
        ;;
        --ui)
        RUN_API=false
        RUN_UI=true
        shift
        ;;
        --cov)
        COVERAGE=true
        shift
        ;;
        --parallel)
        PARALLEL=true
        shift
        ;;
        --verbose)
        VERBOSE=true
        shift
        ;;
        --html)
        HTML_REPORT=true
        shift
        ;;
        --random)
        RANDOM=true
        shift
        ;;
        --env=*)
        ENV_FILE="${arg#*=}"
        if [ -f "$ENV_FILE" ]; then
            echo -e "${YELLOW}加载自定义环境变量: $ENV_FILE${NC}"
            set -a
            source "$ENV_FILE"
            set +a
        else
            echo -e "${RED}错误: 指定的环境变量文件 $ENV_FILE 不存在!${NC}"
            exit 1
        fi
        shift
        ;;
        *)
        # 未知参数
        shift
        ;;
    esac
done

# 输出测试运行信息
echo -e "${YELLOW}开始运行测试...${NC}"
echo -e "环境: ${GREEN}${ENVIRONMENT:-test}${NC}"
echo -e "API 测试: $([ "$RUN_API" = true ] && echo "${GREEN}启用${NC}" || echo "${RED}禁用${NC}")"
echo -e "UI 测试: $([ "$RUN_UI" = true ] && echo "${GREEN}启用${NC}" || echo "${RED}禁用${NC}")"
echo -e "覆盖率报告: $([ "$COVERAGE" = true ] && echo "${GREEN}启用${NC}" || echo "${RED}禁用${NC}")"
echo -e "并行执行: $([ "$PARALLEL" = true ] && echo "${GREEN}启用${NC}" || echo "${RED}禁用${NC}")"
echo -e "详细输出: $([ "$VERBOSE" = true ] && echo "${GREEN}启用${NC}" || echo "${RED}禁用${NC}")"
echo -e "HTML报告: $([ "$HTML_REPORT" = true ] && echo "${GREEN}启用${NC}" || echo "${RED}禁用${NC}")"
echo -e "随机顺序: $([ "$RANDOM" = true ] && echo "${GREEN}启用${NC}" || echo "${RED}禁用${NC}")"
echo ""

# 构建测试命令
CMD="python -m pytest"

# 设置测试范围
TEST_PATHS=""
if [ "$RUN_API" = true ] && [ "$RUN_UI" = false ]; then
    TEST_PATHS="${TEST_API_PATH:-tests/api}"
elif [ "$RUN_API" = false ] && [ "$RUN_UI" = true ]; then
    TEST_PATHS="${TEST_UI_PATH:-tests/ui}"
else
    TEST_PATHS="${TEST_DEFAULT_PATH:-tests}"
fi

# 设置参数
if [ "$VERBOSE" = true ]; then
    CMD="$CMD -v"
fi

if [ "$PARALLEL" = true ]; then
    # 使用环境变量中的worker数量，如果设置为auto则不指定数量
    if [ "${TEST_PARALLEL_WORKERS}" = "auto" ]; then
        CMD="$CMD -n auto"
    else
        CMD="$CMD -n ${TEST_PARALLEL_WORKERS:-auto}"
    fi
fi

if [ "$RANDOM" = true ]; then
    # 如果有设置随机种子，则使用它
    if [ -n "${TEST_RANDOM_SEED}" ]; then
        CMD="$CMD --random-order --random-order-seed=${TEST_RANDOM_SEED}"
    else
        CMD="$CMD --random-order"
    fi
fi

if [ "$COVERAGE" = true ]; then
    # 使用环境变量定义的路径
    BACKEND_PATH="${BACKEND_COV_PATH:-backend}"
    FRONTEND_PATH="${FRONTEND_COV_PATH:-frontend}"
    COV_REPORT_DIR="${COVERAGE_REPORT_DIR:-tests/coverage_html_report}"
    
    CMD="$CMD --cov=$BACKEND_PATH --cov=$FRONTEND_PATH --cov-report=term"
    
    if [ "$HTML_REPORT" = true ]; then
        CMD="$CMD --cov-report=html:$COV_REPORT_DIR"
    fi
elif [ "$HTML_REPORT" = true ]; then
    HTML_PATH="${HTML_REPORT_PATH:-report.html}"
    CMD="$CMD --html=$HTML_PATH"
fi

# 执行测试
echo -e "${YELLOW}执行命令: ${NC}$CMD $TEST_PATHS"
$CMD $TEST_PATHS

# 输出测试结果
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}测试成功通过!${NC}"
    if [ "$COVERAGE" = true ] && [ "$HTML_REPORT" = true ]; then
        echo -e "${GREEN}覆盖率报告保存在: ${COV_REPORT_DIR}${NC}"
    elif [ "$HTML_REPORT" = true ]; then
        echo -e "${GREEN}HTML报告保存在: ${HTML_PATH}${NC}"
    fi
else
    echo -e "\n${RED}测试失败，退出代码: $EXIT_CODE${NC}"
fi

exit $EXIT_CODE 