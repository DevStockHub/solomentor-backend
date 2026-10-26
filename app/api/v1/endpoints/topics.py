from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud.session_plan import update_topic
from app.schemas.session_plan import TopicUpdate, TopicOut

router = APIRouter()


@router.put("/{topic_id}", response_model=TopicOut)
async def update_topic_endpoint(topic_id: str, topic_in: TopicUpdate, db: AsyncSession = Depends(get_db)):
    topic = await update_topic(db, topic_id, topic_in)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic