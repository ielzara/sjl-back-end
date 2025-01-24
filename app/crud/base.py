from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for CRUD operations.
    
    Args:
        ModelType: SQLAlchemy model class
        CreateSchemaType: Pydantic model for creation
        UpdateSchemaType: Pydantic model for updates
    """
    
    def __init__(self, model: Type[ModelType]):
        """Initialize CRUD object.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Optional[ModelType]: Record if found, None otherwise
        """
        query = select(self.model).filter(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi_paginated(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filter_query: Optional[Select] = None
    ) -> Tuple[List[ModelType], int, bool]:
        """Get multiple records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filter_query: Optional SQLAlchemy select query for filtering
            
        Returns:
            Tuple containing:
            - List[ModelType]: List of records
            - int: Total count of records
            - bool: Whether there are more records
        """
        # Use provided filter query or create default
        query = filter_query if filter_query is not None else select(self.model)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)

        # Apply pagination
        query = query.offset(skip).limit(limit + 1)
        result = await db.execute(query)
        items = result.scalars().all()

        # Check if there are more items
        has_more = len(items) > limit
        items = items[:limit]
        
        return items, total, has_more

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record.
        
        Args:
            db: Database session
            obj_in: Pydantic model or dict with create data
            
        Returns:
            ModelType: Created record
            
        Raises:
            Exception: If creation fails
        """
        try:
            if isinstance(obj_in, dict):
                create_data = obj_in
            else:
                create_data = obj_in.model_dump()

            db_obj = self.model(**create_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            print("Error in create:", str(e))
            raise
        
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update a record.
        
        Args:
            db: Database session
            db_obj: Existing record to update
            obj_in: Pydantic model or dict with update data
            
        Returns:
            ModelType: Updated record
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        """Delete a record.
        
        Args:
            db: Database session
            id: Record ID to delete
            
        Returns:
            ModelType: Deleted record
        """
        obj = await self.get(db=db, id=id)
        await db.delete(obj)
        await db.commit()
        return obj