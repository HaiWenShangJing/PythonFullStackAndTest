# Full-Stack AI CRUD Application

A comprehensive full-stack application that combines database CRUD operations with AI chat capabilities.

## Features

- FastAPI backend with async SQLAlchemy ORM
- Streamlit frontend with interactive UI
- PostgreSQL database with Alembic migrations
- AI chat integration with OpenRouter API
- Docker-based deployment
- Comprehensive test suite
- CI/CD pipeline with GitHub Actions

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Poetry (for dependency management)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fullstack-ai-crud.git
cd fullstack-ai-crud
```

2. Install dependencies:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

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

## Architecture

See [Architecture Documentation](docs/architecture.md) for details on the system design.

## License

This project is licensed under the MIT License - see the LICENSE file for details.