from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


# Item schemas
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    name: Optional[str] = None


class ItemResponse(ItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ItemsListResponse(BaseModel):
    items: List[ItemResponse]
    total: int


# AI Chat schemas
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[UUID] = None
    context: Optional[List[dict]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    message: str
    session_id: UUID


# User schemas for future expansion
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True