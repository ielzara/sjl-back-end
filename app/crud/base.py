from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        '''
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        '''
        self.model = model

    async def get(self, db: AsuncSession, id: Any) -> Optional[ModelType]:
        '''
        get a single record by id
        **Parameters**
        * `db`: AsyncSession instance
        * `id`: record id
        **Returns**
        * record instance
        '''

        query = select(self.model).filter(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi_paginated(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Tuple[List[ModelType], int, bool]:
        '''
        get multiple records with pagination
        **Parameters**
        *`db`: AsyncSession instance
        * `skip`: number of records to skip
        * `limit`: number of records to return
        **Returns**
        * Tuple of (list of records, total count and has_more flag)
        '''

        # Get total count
        count_query = select(func.count()).select_from(self.model)
        total = await db.scalar(count_query)

        # Get one extra item to check if there are more records
        query = select(self.model).offset(skip).limit(limit + 1)
        result = await dv.execute(query)
        items = result.scalars().all()

        # Check if there are more records
        has_more = len(items) > limit
        items = items[:limit]
        return items, total, has_more

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        '''
        create a new record
        ** Parameters**
        * `db`: AsyncSession instance
        * `obj_in`: Pydantic model instance
        **Returns**
        * record instance
        '''
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        '''
        update a record
        **Parameters**
        * `db`: AsyncSession instance
        * `db_obj`: record instance
        * `obj_in`: Pydantic model instance or dictionary
        **Returns**
        * record instance
        '''
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
        '''
        delete a record
        **Parameters**
        * `db`: AsyncSession instance
        * `id`: record id
        **Returns**
        * record instance
        '''

        obj = await self.get(db=db, id=id)
        await db.delete(obj)
        await db.commit()
        return obj