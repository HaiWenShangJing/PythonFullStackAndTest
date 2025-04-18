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
- **完善测试体系**：包含单元测试、集成测试和端到端测试
- **自动化流程**：GitHub Actions实现CI/CD，自动化测试和部署

## 开始使用

### 系统要求

- Python 3.10+
- Docker 和 Docker Compose
- Poetry (依赖管理工具)

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
- `SECRET_KEY`: 应用加密密钥
- `DEBUG`: 调试模式开关(true/false)

### Running the Application

#### Local Development

1. Start the PostgreSQL database:
```bash
docker-compose up -d db
```

2. Run database migrations:
```bash
poetry run alembic upgrade head
```

3. Start the backend server:
```bash
poetry run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

4. In a separate terminal, start the frontend:
```bash
poetry run streamlit run frontend/streamlit_app.py
```

#### Using Docker Compose

```bash
docker-compose up -d
```

Access:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Database Migrations

To create a new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

To apply migrations:
```bash
poetry run alembic upgrade head
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=backend --cov=frontend

# Run specific test categories
poetry run pytest tests/api
poetry run pytest tests/ui
```

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
├── infra/              # 基础设施配置
└── tests/              # 测试套件
```

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

## 许可证

本项目采用MIT许可证 - 详情请参阅LICENSE文件。