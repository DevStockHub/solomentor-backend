from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.mentor_profile import MentorProfile
from app.schemas.mentor_profile import MentorProfileCreate, MentorProfileUpdate


async def get_mentor_profile(db: AsyncSession, profile_id: str) -> MentorProfile | None:
    result = await db.execute(select(MentorProfile).where(MentorProfile.id == profile_id))
    return result.scalar_one_or_none()


async def get_first_mentor_profile(db: AsyncSession) -> MentorProfile | None:
    result = await db.execute(select(MentorProfile).order_by(MentorProfile.created_at.asc()).limit(1))
    return result.scalar_one_or_none()


async def get_mentor_profile_by_name(db: AsyncSession, name: str) -> MentorProfile | None:
    result = await db.execute(select(MentorProfile).where(MentorProfile.name == name))
    return result.scalar_one_or_none()


async def create_mentor_profile(db: AsyncSession, profile_in: MentorProfileCreate) -> MentorProfile:
    db_obj = MentorProfile(**profile_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_mentor_profile(db: AsyncSession, profile_id: str, profile_in: MentorProfileUpdate) -> MentorProfile | None:
    db_obj = await get_mentor_profile(db, profile_id)
    if not db_obj:
        return None
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj