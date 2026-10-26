from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


async def get_student(db: AsyncSession, student_id: str) -> Student | None:
    result = await db.execute(select(Student).where(Student.id == student_id))
    return result.scalar_one_or_none()


async def get_students_by_mentor(db: AsyncSession, mentor_id: str, skip: int = 0, limit: int = 100) -> list[Student]:
    result = await db.execute(
        select(Student).where(Student.mentor_id == mentor_id).order_by(Student.name.asc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_all_students(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Student]:
    result = await db.execute(
        select(Student).order_by(Student.name.asc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def create_student(db: AsyncSession, student_in: StudentCreate, mentor_id: str) -> Student:
    data = student_in.model_dump(exclude={"mentor_id"})
    db_obj = Student(**data, mentor_id=mentor_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_student(db: AsyncSession, student_id: str, student_in: StudentUpdate) -> Student | None:
    db_obj = await get_student(db, student_id)
    if not db_obj:
        return None
    update_data = student_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_student(db: AsyncSession, student_id: str) -> bool:
    db_obj = await get_student(db, student_id)
    if not db_obj:
        return False
    await db.delete(db_obj)
    await db.commit()
    return True