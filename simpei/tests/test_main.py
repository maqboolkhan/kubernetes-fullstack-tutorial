"""Tests for the todo list API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.simpei.database import Base, get_db
from src.simpei.main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_read_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Simpei Todo API"}


def test_create_todo():
    """Test creating a todo item."""
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo",
        "completed": False
    }
    response = client.post("/todos/", json=todo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == todo_data["title"]
    assert data["description"] == todo_data["description"]
    assert data["completed"] == todo_data["completed"]
    assert "id" in data
    assert "created_at" in data


def test_get_todos():
    """Test getting all todos."""
    response = client.get("/todos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_todo_by_id():
    """Test getting a specific todo by ID."""
    # First create a todo
    todo_data = {"title": "Test Todo for Get", "description": "Test description"}
    create_response = client.post("/todos/", json=todo_data)
    todo_id = create_response.json()["id"]
    
    # Then get it by ID
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == todo_data["title"]


def test_update_todo():
    """Test updating a todo item."""
    # First create a todo
    todo_data = {"title": "Todo to Update", "completed": False}
    create_response = client.post("/todos/", json=todo_data)
    todo_id = create_response.json()["id"]
    
    # Then update it
    update_data = {"title": "Updated Todo", "completed": True}
    response = client.put(f"/todos/{todo_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["completed"] == update_data["completed"]


def test_delete_todo():
    """Test deleting a todo item."""
    # First create a todo
    todo_data = {"title": "Todo to Delete"}
    create_response = client.post("/todos/", json=todo_data)
    todo_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404


def test_get_todos_by_status():
    """Test getting todos by completion status."""
    # Create completed and incomplete todos
    client.post("/todos/", json={"title": "Completed Todo", "completed": True})
    client.post("/todos/", json={"title": "Incomplete Todo", "completed": False})
    
    # Test getting completed todos
    response = client.get("/todos/completed/true")
    assert response.status_code == 200
    completed_todos = response.json()
    assert all(todo["completed"] for todo in completed_todos)
    
    # Test getting incomplete todos
    response = client.get("/todos/completed/false")
    assert response.status_code == 200
    incomplete_todos = response.json()
    assert all(not todo["completed"] for todo in incomplete_todos)
