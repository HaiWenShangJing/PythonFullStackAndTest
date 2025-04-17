from typing import List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Base, Item

# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase:
    """Base class for CRUD operations"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get a record by ID"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()
    
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination"""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def count(self, db: AsyncSession) -> int:
        """Count total records"""
        result = await db.execute(select(func.count(self.model.id)))
        return result.scalar()
    
    async def create(self, db: AsyncSession, *, obj_in) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in) -> ModelType:
        """Update a record"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: UUID) -> Optional[ModelType]:
        """Delete a record"""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


# Create CRUD instance for Item model
item_crud = CRUDBase(Item)