# Simpei

A simple todo list API that just works, hopefully! Built with FastAPI and SQLite.

## Features

- ✅ Create, read, update, and delete todos
- ✅ Filter todos by completion status
- ✅ RESTful API with automatic OpenAPI documentation
- ✅ SQLite database with SQLAlchemy ORM
- ✅ CORS support for frontend integration
- ✅ Docker support
- ✅ Comprehensive test suite
- ✅ Code quality tools (ruff, mypy, pre-commit)

## Quick Start

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/maqboolkhan/simpei.git
cd simpei
```

2. Install dependencies:
```bash
make install
```

3. Run the development server:
```bash
make run
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| POST | `/todos/` | Create a new todo |
| GET | `/todos/` | Get all todos (with pagination) |
| GET | `/todos/{id}` | Get a specific todo |
| PUT | `/todos/{id}` | Update a todo |
| DELETE | `/todos/{id}` | Delete a todo |
| GET | `/todos/completed/{status}` | Get todos by completion status |


## Development

### Available Commands

```bash
make install      # Install dependencies and pre-commit hooks
make run          # Start the development server
make test         # Run tests
make check        # Run code quality checks
make build        # Build wheel package
```

### Code Quality

This project uses several tools to maintain code quality:
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checking
- **pre-commit**: Git hooks for code quality
- **pytest**: Testing framework

Run all checks:
```bash
make check
```

### Testing

Run the test suite:
```bash
make test
```

Tests are located in the `tests/` directory and cover all API endpoints.

## Docker

### Build and run with Docker:

```bash
make docker-build
make docker-run
```

## Project Structure

```
simpei/
├── src/simpei/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── database.py      # Database models and connection
│   └── schemas.py       # Pydantic schemas
├── tests/
│   └── test_main.py     # API tests
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml       # Project configuration
├── Makefile            # Development commands
└── README.md
```

## Configuration

The application uses SQLite by default and stores the database file as `todos.db` in the project root. The database is automatically created when the application starts.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks: `make check test`
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is open source. See the repository for license details.