from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple, Sequence
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, func, Select, or_
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
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

    async def search(
        self,
        db: AsyncSession,
        *,
        keyword: str,
        fields: Sequence[str],
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[ModelType], int, bool]:
        """
        Generic search across specified model fields
        
        Args:
            db: Database session
            keyword: Search term
            fields: List of model fields to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple containing:
            - List of matching records
            - Total count
            - Boolean indicating if there are more records
        """
        try:
            if not keyword:
                return await self.get_multi_paginated(db, skip=skip, limit=limit)

            # Create conditions for each field
            conditions = []
            for field in fields:
                if hasattr(self.model, field):
                    field_obj = getattr(self.model, field)
                    conditions.append(field_obj.ilike(f"%{keyword}%"))

            if not conditions:
                logger.warning(f"No searchable fields found among {fields}")
                return [], 0, False

            # Combine conditions with OR
            filter_query = select(self.model).filter(or_(*conditions))
            return await self.get_multi_paginated(
                db, 
                skip=skip, 
                limit=limit,
                filter_query=filter_query
            )

        except Exception as e:
            logger.error(f"Error searching {self.model.__name__}: {str(e)}")
            raise ValueError(f"Unable to search {self.model.__name__}")

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
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
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
        
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        try:
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
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        try:
            obj = await self.get(db=db, id=id)
            await db.delete(obj)
            await db.commit()
            return obj
        except Exception as e:
            await db.rollback()
            logger.error(f"Error removing {self.model.__name__}: {str(e)}")
            raise