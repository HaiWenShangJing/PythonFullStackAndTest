# 开发者指南

## 简介

本文档为全栈AI CRUD应用的开发者提供详细的技术指南，包括环境设置、代码规范、架构说明和贡献流程。无论您是项目的新成员还是外部贡献者，本指南都将帮助您快速理解项目结构并开始有效贡献。

## 开发环境设置

### 本地开发环境

1. **克隆代码库**
   ```bash
   git clone https://github.com/HaiWenShangJing/PythonFullStackAndTest.git
   cd PythonFullStackAndTest
   ```

2. **安装依赖**
   ```bash
   # 安装Poetry（如果尚未安装）
   curl -sSL https://install.python-poetry.org | python3 -
   
   # 安装项目依赖
   poetry install
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑.env文件，填入必要的配置信息
   ```

4. **启动开发服务器**
   ```bash
   # 启动数据库
   docker-compose up -d db
   
   # 应用数据库迁移
   poetry run alembic upgrade head
   
   # 启动后端服务（终端1）
   poetry run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   
   # 启动前端服务（终端2）
   poetry run streamlit run frontend/streamlit_app.py
   ```

### Docker开发环境

如果您更喜欢使用Docker进行开发：

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问应用
# 前端: http://localhost:8501
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

## 项目结构

```
├── .github/workflows/  # CI/CD配置
│   └── ci_cd.yml       # CI/CD工作流配置文件
├── alembic/            # 数据库迁移脚本
│   ├── versions/       # 迁移版本文件
│   │   └── 001_create_items_table.py  # 初始迁移脚本
│   ├── env.py          # Alembic环境配置
│   └── script.py.mako  # 迁移脚本模板
├── backend/            # 后端API服务
│   └── app/
│       ├── routers/    # API路由定义
│       ├── crud.py     # 数据库操作函数
│       ├── db.py       # 数据库连接管理
│       ├── main.py     # 应用入口
│       ├── models.py   # 数据库模型
│       └── schemas.py  # 数据验证模式
├── docs/               # 项目文档
│   ├── architecture.md # 系统架构文档
│   ├── developer_guide.md # 开发者指南
│   └── user_guide.md   # 用户指南
├── frontend/           # Streamlit前端
│   ├── pages/          # 应用页面
│   │   ├── ai_chat.py  # AI聊天页面
│   │   ├── dashboard.py # 仪表盘页面
│   │   └── data_mgmt.py # 数据管理页面
│   └── streamlit_app.py # 前端入口
├── infra/              # 基础设施配置
│   └── k8s/            # Kubernetes配置
│       └── deployment.yaml # K8s部署配置
├── tests/              # 测试套件
│   ├── api/            # API测试
│   │   ├── test_ai.py  # AI功能测试
│   │   └── test_items.py # 数据项测试
│   ├── ui/             # UI测试
│   │   ├── test_ai_assistant.py # AI助手UI测试
│   │   └── test_dashboard.py # 仪表盘UI测试
│   └── conftest.py     # 测试配置和固件
├── .env.example        # 环境变量示例文件
├── Dockerfile          # Docker构建文件
├── docker-compose.yml  # Docker Compose配置
└── pyproject.toml      # 项目依赖和配置
```

## 代码规范

### Python代码风格

- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)代码风格指南
- 使用[Black](https://github.com/psf/black)格式化代码
- 使用[isort](https://pycqa.github.io/isort/)排序导入
- 使用[Flake8](https://flake8.pycqa.org/)进行代码检查

### 类型注解

项目使用Python类型注解提高代码可读性和可维护性：

```python
from typing import List, Optional

def get_items(skip: int = 0, limit: int = 100) -> List[Item]:
    # 函数实现
    pass
```

### 提交信息规范

使用[约定式提交](https://www.conventionalcommits.org/)格式：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

类型包括：
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更改
- `style`: 不影响代码含义的更改（空格、格式等）
- `refactor`: 既不修复错误也不添加功能的代码更改
- `test`: 添加或修正测试
- `chore`: 对构建过程或辅助工具的更改

## 开发工作流

### 功能开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **编写代码和测试**
   - 实现功能
   - 编写单元测试和集成测试
   - 确保所有测试通过

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建Pull Request**
   - 在GitHub上创建PR
   - 等待CI检查和代码审查
   - 根据反馈进行修改

### 数据库迁移

添加或修改数据库模型后，需要创建迁移脚本：

```bash
# 创建迁移脚本
poetry run alembic revision --autogenerate -m "add new field"

# 应用迁移
poetry run alembic upgrade head
```

## 测试指南

### 测试结构

- `tests/api/`: 后端API测试
- `tests/ui/`: 前端UI测试
- `tests/conftest.py`: 测试固件和配置

### 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行特定测试文件
poetry run pytest tests/api/test_items.py

# 运行带标记的测试
poetry run pytest -m "api"

# 生成覆盖率报告
poetry run pytest --cov=backend --cov=frontend --cov-report=html
```

### 编写测试

示例API测试：

```python
async def test_create_item(client, db_session):
    response = await client.post(
        "/api/v1/items/",
        json={"title": "Test Item", "description": "Test Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"
```

## API文档

项目使用FastAPI的自动文档生成功能。启动后端服务后，可以访问以下URL查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 前端开发

### Streamlit组件

Streamlit应用由多个页面组成，每个页面都是一个Python模块。页面之间可以共享状态和会话数据。

示例页面结构：

```python
import streamlit as st
import httpx

st.title("数据管理")

# 获取数据
async def load_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/items/")
        return response.json()

data = st.experimental_data_editor(load_data())

# 添加表单
with st.form("item_form"):
    title = st.text_input("标题")
    description = st.text_area("描述")
    submitted = st.form_submit_button("提交")
    
    if submitted:
        # 处理表单提交
        pass
```

## CI/CD流程

项目使用GitHub Actions进行持续集成和部署：

- 每次推送到主分支时运行测试
- 成功测试后自动构建Docker镜像
- 将镜像推送到容器注册表
- 部署到测试/生产环境

## 故障排除

### 常见开发问题

1. **数据库连接问题**
   - 检查PostgreSQL服务是否运行
   - 验证连接字符串是否正确
   - 确保数据库用户有适当权限

2. **依赖冲突**
   - 使用`poetry show --tree`查看依赖树
   - 更新poetry.lock文件：`poetry update`

3. **前端无法连接后端**
   - 确保后端服务正在运行
   - 检查CORS设置
   - 验证API URL配置

## 性能优化提示

1. **数据库查询优化**
   - 使用适当的索引
   - 避免N+1查询问题
   - 使用异步查询处理并发请求

2. **前端性能**
   - 减少不必要的API调用
   - 使用缓存减少重复计算
   - 实现分页加载大数据集

## 联系与支持

如有开发相关问题，请通过以下方式获取支持：

- 在GitHub上创建Issue
- 加入开发者Slack频道
- 发送邮件至dev-support@example.com

---

感谢您对项目的贡献！如有任何问题或建议，请随时联系项目维护者。