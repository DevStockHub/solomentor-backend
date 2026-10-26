from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


async def get_subject(db: AsyncSession, subject_id: str) -> Subject | None:
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    return result.scalar_one_or_none()


async def get_subject_by_code(db: AsyncSession, code: str) -> Subject | None:
    result = await db.execute(select(Subject).where(Subject.code == code))
    return result.scalar_one_or_none()


async def get_subjects(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Subject]:
    result = await db.execute(select(Subject).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_subject(db: AsyncSession, subject_in: SubjectCreate) -> Subject:
    db_obj = Subject(**subject_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_subject(db: AsyncSession, subject_id: str, subject_in: SubjectUpdate) -> Subject | None:
    db_obj = await get_subject(db, subject_id)
    if not db_obj:
        return None
    update_data = subject_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj