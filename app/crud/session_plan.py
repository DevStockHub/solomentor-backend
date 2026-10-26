from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.session_plan import SessionPlan
from app.models.topic import Topic
from app.schemas.session_plan import SessionPlanCreate, SessionPlanUpdate, TopicCreate, TopicUpdate


async def get_session_plan(db: AsyncSession, plan_id: str) -> SessionPlan | None:
    result = await db.execute(
        select(SessionPlan).where(SessionPlan.id == plan_id).options(selectinload(SessionPlan.topics))
    )
    return result.scalar_one_or_none()


async def get_session_plans_by_student(
    db: AsyncSession, student_id: str, skip: int = 0, limit: int = 100
) -> list[SessionPlan]:
    result = await db.execute(
        select(SessionPlan)
        .where(SessionPlan.student_id == student_id)
        .options(selectinload(SessionPlan.topics))
        .order_by(SessionPlan.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_all_session_plans(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[SessionPlan]:
    result = await db.execute(
        select(SessionPlan)
        .options(selectinload(SessionPlan.topics))
        .order_by(SessionPlan.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_session_plan(db: AsyncSession, plan_in: SessionPlanCreate) -> SessionPlan:
    plan_data = plan_in.model_dump(exclude={"topics"})
    db_obj = SessionPlan(**plan_data)
    db.add(db_obj)
    await db.flush()

    for topic_in in plan_in.topics:
        topic = Topic(**topic_in.model_dump(), session_plan_id=db_obj.id)
        db.add(topic)

    await db.commit()
    loaded_plan = await get_session_plan(db, db_obj.id)
    return loaded_plan  # type: ignore


async def update_session_plan(db: AsyncSession, plan_id: str, plan_in: SessionPlanUpdate) -> SessionPlan | None:
    db_obj = await get_session_plan(db, plan_id)
    if not db_obj:
        return None
    update_data = plan_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    await db.commit()
    return await get_session_plan(db, plan_id)


async def delete_session_plan(db: AsyncSession, plan_id: str) -> bool:
    db_obj = await get_session_plan(db, plan_id)
    if not db_obj:
        return False
    await db.delete(db_obj)
    await db.commit()
    return True


async def get_topic(db: AsyncSession, topic_id: str) -> Topic | None:
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    return result.scalar_one_or_none()


async def update_topic(db: AsyncSession, topic_id: str, topic_in: TopicUpdate) -> Topic | None:
    db_obj = await get_topic(db, topic_id)
    if not db_obj:
        return None
    update_data = topic_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj