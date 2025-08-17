"""Pydantic schemas for todo list API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TodoBase(BaseModel):
    """Base todo schema."""
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoCreate(TodoBase):
    """Schema for creating a todo item."""
    pass


class TodoUpdate(BaseModel):
    """Schema for updating a todo item."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(TodoBase):
    """Schema for todo item response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True