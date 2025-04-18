# 测试框架说明

本项目使用 pytest 作为测试框架，包含 API 测试和 UI 测试两部分。所有测试配置均通过环境变量进行管理，支持高度定制和灵活配置。

## 目录结构

```
tests/
├── api/                    # API测试
│   ├── test_ai.py          # AI API测试
│   └── test_items.py       # Items API测试
├── ui/                     # UI测试
│   ├── pages/              # 页面对象模型
│   │   ├── base_page.py
│   │   ├── ai_assistant_page.py
│   │   └── ...
│   ├── conftest.py         # UI测试配置
│   ├── test_ai_assistant.py
│   └── ...
├── conftest.py             # 全局测试配置
├── .env.test               # 测试环境变量
├── .env.example            # 环境变量示例与说明
├── requirements-test.txt   # 测试依赖
├── run_tests.sh            # Linux/MacOS测试脚本
├── run_tests.ps1           # Windows PowerShell测试脚本
├── run_tests.bat           # Windows命令提示符测试脚本
└── README.md               # 本文档
```

## 环境变量配置

测试框架使用 `.env.test` 文件来管理所有配置。我们提供了 `.env.example` 作为模板，包含所有可配置项的说明和默认值。

### 创建测试环境配置

1. 复制环境变量示例文件：
   ```bash
   cp tests/.env.example tests/.env.test
   ```

2. 根据需要编辑 `.env.test` 文件，至少需要设置以下必需变量：
   - `DATABASE_URL` - 测试数据库连接字符串
   - `OPENROUTER_API_KEY` - AI服务API密钥
   - `STREAMLIT_URL` - Streamlit应用URL（用于UI测试）

### 主要配置组

环境变量配置分为以下几个主要部分：

#### 基础配置
```
ENVIRONMENT=test           # 环境名称
TEST_MODE=local            # 测试模式，可选：local, ci
```

#### AI服务配置
```
OPENROUTER_API_KEY=***     # AI服务API密钥
OPENROUTER_API_URL=***     # AI服务API URL
MODEL_NAME=***             # 使用的模型名称
API_TIMEOUT=30             # API请求超时时间（秒）
```

#### 错误消息配置
```
AI_SERVICE_ERROR_MSG=AI服务暂时无法使用  # 服务错误消息
AI_FALLBACK_MSG=我是AI助手              # 后备消息
AI_CREDITS_ERROR_MSG=积分不足           # 积分不足错误消息
```

#### 测试执行配置
```
TEST_PARALLEL_WORKERS=auto # 并行worker数量，'auto'或具体数字
TEST_RANDOM_SEED=42        # 随机种子，确保可重现性
COVERAGE=false             # 是否默认启用覆盖率报告
TEST_PARALLEL=false        # 是否默认启用并行测试
```

#### UI测试配置
```
PAGE_LOAD_TIMEOUT=30       # 页面加载超时时间（秒）
AI_RESPONSE_TIMEOUT=30     # AI响应超时时间（秒）
```

完整的配置列表请参考 `.env.example` 文件。

## 安装测试依赖

```bash
pip install -r tests/requirements-test.txt
```

## 运行测试

我们提供了三种平台的测试运行脚本，支持多种运行模式和参数配置：

### Linux/MacOS:

```bash
# 运行所有测试
./run_tests.sh

# 仅运行API测试
./run_tests.sh --api

# 仅运行UI测试
./run_tests.sh --ui

# 带覆盖率报告
./run_tests.sh --cov

# 使用多进程加速测试
./run_tests.sh --parallel

# 使用随机顺序
./run_tests.sh --random

# 生成HTML报告
./run_tests.sh --html

# 使用详细输出
./run_tests.sh --verbose

# 使用自定义环境变量文件
./run_tests.sh --env=./tests/.env.production

# 组合使用
./run_tests.sh --api --cov --verbose
```

### Windows (PowerShell):

```powershell
# 运行所有测试
.\tests\run_tests.ps1

# 参数使用与Linux/MacOS相同
.\tests\run_tests.ps1 --api --cov
```

### Windows (命令提示符):

```cmd
# 运行所有测试
run_tests.bat

# 参数使用与Linux/MacOS相同
run_tests.bat --api --cov
```

## 测试脚本高级功能

测试运行脚本提供了多种功能来帮助你灵活地运行测试：

### 使用自定义环境变量

你可以为不同的测试环境创建多个环境变量文件，例如 `.env.dev`, `.env.staging` 等，并通过 `--env` 参数指定使用哪个环境：

```bash
./run_tests.sh --env=./tests/.env.staging
```

### 测试结果与报告

- **覆盖率报告**：使用 `--cov` 参数生成代码覆盖率报告，位置可在 `.env.test` 中的 `COVERAGE_REPORT_DIR` 配置
- **HTML测试报告**：使用 `--html` 参数生成HTML测试报告，位置可在 `.env.test` 中的 `HTML_REPORT_PATH` 配置

### 并行测试加速

使用 `--parallel` 参数开启并行测试，可以大幅提高测试执行速度。并行工作进程数量可在 `.env.test` 中的 `TEST_PARALLEL_WORKERS` 配置：

```
# 自动检测CPU核心数
TEST_PARALLEL_WORKERS=auto

# 或指定特定数量
TEST_PARALLEL_WORKERS=4
```

### 随机测试顺序

使用 `--random` 参数以随机顺序执行测试，有助于发现测试之间的依赖问题。为确保可重现性，可以在 `.env.test` 中设置 `TEST_RANDOM_SEED`。

## 测试标记

使用`pytest.mark`装饰器标记测试类型：

```python
@pytest.mark.api
@pytest.mark.asyncio
async def test_something():
    # API测试...

@pytest.mark.ui
def test_ui_feature():
    # UI测试...

@pytest.mark.unit
def test_unit():
    # 单元测试...

@pytest.mark.integration
def test_integration():
    # 集成测试...
```

## 直接运行特定测试

如果需要更精细控制，可以直接使用pytest命令：

```bash
# 运行特定测试文件
python -m pytest tests/api/test_ai.py

# 运行特定测试函数
python -m pytest tests/api/test_ai.py::test_chat_with_ai

# 运行特定标记的测试
python -m pytest -m "api and not slow"

# 使用表达式筛选测试
python -m pytest -k "chat or message"
```

## UI测试说明

UI测试使用Selenium WebDriver，需要配置浏览器驱动。在CI环境中，使用Selenium Grid进行测试。

设置方法：
1. 在 `.env.test` 中设置 `SELENIUM_HUB_URL` 和 `STREAMLIT_URL`
2. 确保浏览器驱动可用

可配置的UI测试超时参数：
- `PAGE_LOAD_TIMEOUT` - 页面加载超时时间（秒）
- `AI_RESPONSE_TIMEOUT` - AI响应超时时间（秒）
- `PAGE_RELOAD_TIMEOUT` - 页面重新加载超时时间（秒）
- `VALIDATION_TIMEOUT` - 表单验证延迟时间（秒）
- `LONG_MSG_TIMEOUT` - 长消息处理超时时间（秒）

## 自定义测试数据

UI测试中使用的测试消息和数据可以通过环境变量自定义：
```
TEST_AI_MESSAGE=Hello, AI assistant!
TEST_CLEAR_MESSAGE=Test message for clearing
TEST_LONG_MSG_WORD=Test
TEST_LONG_MSG_REPEAT=100
TEST_MSG_1=First test message
TEST_MSG_2=Second test message
TEST_MSG_3=Third test message
```

## CI集成指南

在CI环境中运行测试时，建议设置以下环境变量：
- `TEST_MODE=ci` - 启用CI特定的配置
- `TEST_PARALLEL=true` - 启用并行测试以加速CI流程
- `COVERAGE=true` - 生成覆盖率报告
- `TEST_RANDOM=true` - 随机测试顺序增强测试健壮性

CI配置示例：
```yaml
test:
  stage: test
  script:
    - cp tests/.env.example tests/.env.test
    - echo "TEST_MODE=ci" >> tests/.env.test
    - echo "OPENROUTER_API_KEY=$CI_OPENROUTER_API_KEY" >> tests/.env.test
    - ./run_tests.sh --parallel --cov
  artifacts:
    paths:
      - tests/coverage_html_report
```

## 模拟与桩

- 使用`unittest.mock`模拟外部依赖
- API测试中使用`patch`装饰器模拟HTTP请求
- UI测试使用页面对象模型(POM)模式
- 所有硬编码的测试数据已移至环境变量配置 