from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.progress_record import ProgressRecord
from app.schemas.progress_record import ProgressRecordCreate


async def get_progress_records_by_student(
    db: AsyncSession, student_id: str, skip: int = 0, limit: int = 100
) -> list[ProgressRecord]:
    result = await db.execute(
        select(ProgressRecord)
        .where(ProgressRecord.student_id == student_id)
        .order_by(ProgressRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_all_progress_records(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[ProgressRecord]:
    result = await db.execute(
        select(ProgressRecord)
        .order_by(ProgressRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_progress_record(db: AsyncSession, record_in: ProgressRecordCreate, student_id: str) -> ProgressRecord:
    data = record_in.model_dump(exclude={"student_id"})
    db_obj = ProgressRecord(**data, student_id=student_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj