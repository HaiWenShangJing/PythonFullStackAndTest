# Full-Stack AI CRUD Application

一个综合性的全栈应用程序，结合了数据库CRUD操作和AI聊天功能。该项目采用现代化的技术栈，包括FastAPI后端、Streamlit前端、PostgreSQL数据库和OpenRouter AI集成，旨在提供高性能、可扩展的Web应用解决方案。

## 项目概述

本项目是一个完整的全栈应用示例，展示了如何将传统的数据管理功能与先进的AI对话能力无缝集成。系统架构采用前后端分离设计，通过异步处理提高性能，并使用容器化技术简化部署流程。

## 功能特点

- **高性能后端**：FastAPI框架提供异步支持，结合SQLAlchemy ORM实现高效数据操作
- **交互式前端**：Streamlit框架快速构建响应式用户界面，支持数据可视化
- **可靠数据存储**：PostgreSQL数据库配合Alembic迁移工具，确保数据模型版本控制
- **AI对话能力**：集成OpenRouter API，支持多种大型语言模型
- **容器化部署**：Docker和Docker Compose简化环境配置和应用部署
- **完善测试体系**：包含单元测试、集成测试、API测试和UI自动化测试
- **环境变量配置**：所有配置项通过环境变量管理，支持不同环境灵活切换
- **自动化流程**：GitHub Actions实现CI/CD，自动化测试和部署

## 开始使用

### 系统要求

- Python 3.10+
- Docker 和 Docker Compose
- Poetry (依赖管理工具)
- PostgreSQL 13+
- Chrome/Firefox (UI测试)

### 安装步骤

1. 克隆代码仓库:
```bash
git clone https://github.com/HaiWenShangJing/PythonFullStackAndTest.git
cd PythonFullStackAndTest
```

2. 安装依赖:
```bash
poetry install
```

3. 配置环境变量:
```bash
cp .env.example .env
# 编辑.env文件，填入您的配置信息
```

环境变量配置说明:
- `DATABASE_URL`: PostgreSQL连接字符串
- `OPENROUTER_API_KEY`: OpenRouter API密钥
- `OPENROUTER_API_URL`: OpenRouter API URL
- `MODEL_NAME`: 使用的AI模型名称
- `SECRET_KEY`: 应用加密密钥
- `DEBUG`: 调试模式开关(true/false)

完整的环境变量列表请参考 `.env.example` 文件。

### 运行应用程序

#### 本地开发环境

1. 启动PostgreSQL数据库:
```bash
docker-compose up -d db
```

2. 运行数据库迁移:
```bash
poetry run alembic upgrade head
```

3. 启动后端服务:
```bash
poetry run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

4. 在另一个终端中启动前端:
```bash
poetry run streamlit run frontend/streamlit_app.py
```

#### 使用Docker Compose

完整启动所有服务:

```bash
docker-compose up -d
```

访问地址:
- 前端界面: http://localhost:8501
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 数据库迁移

创建新的迁移脚本:
```bash
poetry run alembic revision --autogenerate -m "描述变更内容"
```

应用迁移到数据库:
```bash
poetry run alembic upgrade head
```

回滚到特定版本:
```bash
poetry run alembic downgrade <版本号或相对位置>
```

## 测试框架

本项目采用全面的测试策略，包括单元测试、API测试和UI自动化测试。测试框架使用pytest作为基础，并集成了多种插件以增强功能。

### 测试架构

测试套件分为以下几个主要部分:

- **API测试**: 针对后端API接口的功能测试，验证数据处理和业务逻辑
- **UI测试**: 基于Selenium的前端界面自动化测试，验证用户交互流程
- **单元测试**: 针对独立组件的功能验证
- **集成测试**: 验证多个组件间的协作功能

### 环境变量配置

所有测试配置均通过环境变量管理，支持多环境灵活切换。主要配置组包括:

- **基础配置**: 环境名称、测试模式等
- **数据库配置**: 测试数据库连接信息
- **AI服务配置**: AI服务API密钥、URL等
- **测试执行配置**: 并行执行、随机顺序、覆盖率报告等
- **UI测试配置**: 超时时间、测试数据等

详细的环境变量说明请参考 `tests/.env.example` 文件。

### 设置测试环境

1. 创建测试环境变量文件:
```bash
cp tests/.env.example tests/.env.test
# 编辑 .env.test 文件，设置必要的测试环境变量
```

2. 安装测试依赖:
```bash
pip install -r tests/requirements-test.txt
```

### 运行测试

我们提供了跨平台的测试脚本，支持多种运行模式:

#### Linux/MacOS

```bash
# 运行所有测试
./run_tests.sh

# 仅运行API测试
./run_tests.sh --api

# 仅运行UI测试
./run_tests.sh --ui

# 生成覆盖率报告
./run_tests.sh --cov

# 并行执行测试
./run_tests.sh --parallel

# 随机顺序执行测试
./run_tests.sh --random

# 生成HTML测试报告
./run_tests.sh --html

# 详细输出模式
./run_tests.sh --verbose

# 使用自定义环境变量文件
./run_tests.sh --env=./tests/.env.staging

# 组合使用多个选项
./run_tests.sh --api --cov --parallel --verbose
```

#### Windows (PowerShell)

```powershell
# 运行所有测试
.\tests\run_tests.ps1

# 使用与Linux/MacOS相同的参数选项
.\tests\run_tests.ps1 --api --cov --parallel
```

#### Windows (命令提示符)

```cmd
# 运行所有测试
run_tests.bat

# 使用与Linux/MacOS相同的参数选项
run_tests.bat --api --cov --parallel
```

### 高级测试功能

#### 自定义测试数据

UI测试使用的测试数据可以通过环境变量自定义:
```
TEST_AI_MESSAGE=Hello, AI assistant!
TEST_CLEAR_MESSAGE=Test message for clearing
TEST_LONG_MSG_WORD=Test
TEST_LONG_MSG_REPEAT=100
TEST_MSG_1=First test message
```

#### 并行测试加速

使用 `--parallel` 参数开启并行测试，可配置工作进程数量:
```
TEST_PARALLEL_WORKERS=auto  # 自动检测CPU核心数
TEST_PARALLEL_WORKERS=4     # 指定4个并行进程
```

#### 测试超时控制

UI测试的各种操作超时时间可精确控制:
```
PAGE_LOAD_TIMEOUT=30       # 页面加载超时时间（秒）
AI_RESPONSE_TIMEOUT=30     # AI响应超时时间（秒）
INPUT_TIMEOUT=10           # 输入字段操作超时时间（秒）
```

#### 测试报告生成

生成HTML测试报告和覆盖率报告:
```bash
./run_tests.sh --cov --html
```

报告位置可在环境变量中配置:
```
COVERAGE_REPORT_DIR=tests/coverage_html_report
HTML_REPORT_PATH=tests/reports/test_report.html
```

### 直接使用pytest

如需更精细的控制，可以直接使用pytest命令:

```bash
# 运行特定测试文件
python -m pytest tests/api/test_ai.py

# 运行特定测试函数
python -m pytest tests/api/test_ai.py::test_chat_with_ai

# 运行特定标记的测试
python -m pytest -m "api and not slow"

# 使用表达式筛选测试
python -m pytest -k "chat or message"

# 自定义输出格式
python -m pytest --tb=short -v
```

## CI/CD 集成

本项目已集成GitHub Actions实现持续集成和持续部署，支持自动化测试、构建和部署。

### CI工作流程

CI流程包括以下步骤:

1. **代码检查**: 使用flake8和mypy进行静态代码分析
2. **单元测试**: 执行所有单元测试
3. **API测试**: 执行后端API测试
4. **UI测试**: 执行前端界面自动化测试
5. **覆盖率报告**: 生成并上传测试覆盖率报告
6. **构建容器**: 构建Docker镜像并推送到容器仓库

### CD工作流程

CD流程自动部署到不同环境:

1. **开发环境**: 每次合并到develop分支
2. **测试环境**: 手动触发或定时触发
3. **生产环境**: 合并到main分支并创建发布标签

### 配置CI环境

在GitHub仓库中设置以下密钥:

- `DATABASE_URL`: CI测试数据库连接字符串
- `OPENROUTER_API_KEY`: OpenRouter API密钥
- `DOCKER_USERNAME`: Docker Hub用户名
- `DOCKER_PASSWORD`: Docker Hub密码

## 系统架构

查看[架构文档](docs/architecture.md)了解系统设计详情。

## 项目结构

```
├── .github/workflows/  # CI/CD配置
├── alembic/            # 数据库迁移脚本
├── backend/            # 后端API服务
│   └── app/
│       ├── routers/    # API路由定义
│       ├── crud.py     # 数据库操作函数
│       ├── db.py       # 数据库连接管理
│       ├── main.py     # 应用入口
│       ├── models.py   # 数据库模型
│       └── schemas.py  # 数据验证模式
├── docs/               # 项目文档
├── frontend/           # Streamlit前端
│   ├── pages/          # 应用页面
│   └── streamlit_app.py # 前端入口
├── tests/              # 测试套件
│   ├── api/            # API测试
│   ├── ui/             # UI测试
│   │   └── pages/      # 页面对象模型
│   ├── conftest.py     # 测试配置
│   ├── .env.example    # 测试环境变量示例
│   ├── run_tests.sh    # Linux/MacOS测试脚本
│   ├── run_tests.ps1   # Windows PowerShell测试脚本
│   └── run_tests.bat   # Windows命令提示符测试脚本
├── infra/              # 基础设施配置
├── .env.example        # 环境变量示例
├── docker-compose.yml  # Docker Compose配置
├── pyproject.toml      # 依赖管理配置
└── README.md           # 本文档
```

## 常见问题排解

### 数据库连接问题

**问题**: 无法连接到数据库
**解决方案**: 
- 检查DATABASE_URL环境变量是否正确
- 确认PostgreSQL服务是否运行
- 验证数据库用户权限是否正确

### 测试失败

**问题**: UI测试失败
**解决方案**:
- 检查Selenium WebDriver是否正确配置
- 增加页面加载超时时间 (PAGE_LOAD_TIMEOUT)
- 检查测试环境中的浏览器兼容性

### AI服务问题

**问题**: AI聊天功能不工作
**解决方案**:
- 验证OPENROUTER_API_KEY是否有效
- 检查网络连接是否正常
- 查看API调用配额是否已用尽

## 贡献指南

我们欢迎各种形式的贡献，包括但不限于功能改进、bug修复、文档更新和测试用例编写。

### 贡献流程

1. Fork项目仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 代码规范

- 遵循PEP 8 Python代码风格指南
- 为所有新功能编写测试
- 保持代码覆盖率在80%以上
- 使用类型注解提高代码可读性
- 遵循项目现有的命名和结构约定

### 测试准则

- 添加新功能时必须包含对应的测试
- 修改现有功能时需更新相关测试
- 确保所有测试都能在不同环境中通过
- 测试应该独立且可重复执行

## 版本历史

- **1.0.0** (2023-06-01): 初始版本发布
- **1.1.0** (2023-07-15): 添加AI聊天功能
- **1.2.0** (2023-09-01): 增强UI功能，改进测试框架
- **1.3.0** (2023-11-15): 完全环境变量配置，优化测试流程

## 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件。

## 联系方式

- 项目维护者: example@example.com
- 项目仓库: https://github.com/yourusername/your-repo
- 问题反馈: https://github.com/yourusername/your-repo/issues