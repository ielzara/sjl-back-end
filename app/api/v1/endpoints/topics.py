from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.topic import topic_crud
from app.schemas.topic import TopicCreate, TopicUpdate, TopicDB, TopicWithCountsDB
from app.schemas.base import BasePaginationResponseSchema
from app.core.database import get_db

router = APIRouter()

@router.get("", response_model=BasePaginationResponseSchema[TopicWithCountsDB])
async def get_topics(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    include_counts: bool = False
) -> BasePaginationResponseSchema[TopicWithCountsDB]:
    '''
    get topics with pagination and optional filtering
    **Parameters**
    * `db`: AsyncSession instance
    * `skip`: number of topics to skip
    * `limit`: number of topics to return
    * `keyword`: search keyword
    * `include_counts`: whether to include article and book counts
    **Returns**
    * paginated response of topic instances
    '''
    if include_counts:
        items, total, has_more = await topic_crud.get_with_counts(
            db, skip=skip, limit=limit
        )
    elif keyword:
        items, total, has_more = await topic_crud.search(
            db, keyword=keyword, skip=skip, limit=limit
        )
    else:
        items, total, has_more = await topic_crud.get_multi_paginated(
            db, skip=skip, limit=limit
        )

    return BasePaginatedResponseSchema(
        total=total,
        items=items,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get("/{topic_id}", response_model=TopicDB)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
) -> TopicDB:
    '''
    get a specific topic by id
    **Parameters**
    * `topic_id`: topic id
    * `db`: AsyncSession instance
    **Returns**
    * topic instance
    '''
    topic = await topic_crud.get(db, id=topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.get("/name/{name}", response_model=TopicDB)
async def get_topic_by_name(
    name: str,
    db: AsyncSession = Depends(get_db)
) -> TopicDB:
    '''
    get a specific topic by name
    **Parameters**
    * `name`: topic name
    * `db`: AsyncSession instance
    **Returns**
    * topic instance
    '''
    topic = await topic_crud.get_by_name(db, name=name)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.post("", response_model=TopicDB, status_code=201)
async def create_topic(
    topic_in: TopicCreate,
    db: AsyncSession = Depends(get_db)
) -> TopicDB:
    '''
    create a new topic
    **Parameters**
    * `topic_in`: TopicCreate instance
    * `db`: AsyncSession instance
    **Returns**
    * topic instance
    '''
    # Check if topic with same name already exists
    existing_topic = await topic_crud.get_by_name(db, name=topic_in.name)
    if existing_topic:
        raise HTTPException(
            status_code=400,
            detail="Topic with this name already exists"
        )
    return await topic_crud.create(db, obj_in=topic_in)

@router.put("/{topic_id}", response_model=TopicDB)
async def update_topic(
    topic_id: int,
    topic_in: TopicUpdate,
    db: AsyncSession = Depends(get_db)
) -> TopicDB:
    '''
    update an existing topic
    **Parameters**
    * `topic_id`: topic id
    * `topic_in`: TopicUpdate instance
    * `db`: AsyncSession instance
    **Returns**
    * topic instance
    '''
    topic = await topic_crud.get(db, id=topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # If name is being updated, check for duplicates
    if topic_in.name:
        existing_topic = await topic_crud.get_by_name(db, name=topic_in.name)
        if existing_topic and existing_topic.id != topic_id:
            raise HTTPException(
                status_code=400,
                detail="Topic with this name already exists"
            )
    
    return await topic_crud.update(db, db_obj=topic, obj_in=topic_in)

@router.delete("/{topic_id}", status_code=204)
async def delete_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
):
    '''
    delete an existing topic
    **Parameters**
    * `topic_id`: topic id
    * `db`: AsyncSession instance
    '''
    topic = await topic_crud.get(db, id=topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    await topic_crud.remove(db, id=topic_id)