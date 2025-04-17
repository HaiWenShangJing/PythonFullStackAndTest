from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud import item_crud
from backend.app.db import get_session
from backend.app.schemas import (
    ItemCreate,
    ItemResponse,
    ItemsListResponse,
    ItemUpdate,
)

router = APIRouter()


@router.get("/items", response_model=ItemsListResponse)
async def read_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_session),
):
    """Get all items with pagination"""
    items = await item_crud.get_multi(db, skip=skip, limit=limit)
    total = await item_crud.count(db)
    return {"items": items, "total": total}


@router.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_session),
):
    """Create a new item"""
    return await item_crud.create(db, obj_in=item)


@router.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_session),
):
    """Get an item by ID"""
    item = await item_crud.get(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    item: ItemUpdate,
    db: AsyncSession = Depends(get_session),
):
    """Update an item"""
    db_item = await item_crud.get(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return await item_crud.update(db, db_obj=db_item, obj_in=item)


@router.delete("/items/{item_id}", response_model=ItemResponse)
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_session),
):
    """Delete an item"""
    db_item = await item_crud.delete(db, id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return db_item