from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.session_note import SessionNote
from app.schemas.session_note import SessionNoteCreate, SessionNoteUpdate


async def get_session_note(db: AsyncSession, note_id: str) -> SessionNote | None:
    result = await db.execute(select(SessionNote).where(SessionNote.id == note_id))
    return result.scalar_one_or_none()


async def get_session_notes_by_plan(
    db: AsyncSession, plan_id: str, skip: int = 0, limit: int = 100
) -> list[SessionNote]:
    result = await db.execute(
        select(SessionNote)
        .where(SessionNote.session_plan_id == plan_id)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_session_note(db: AsyncSession, note_in: SessionNoteCreate) -> SessionNote:
    db_obj = SessionNote(**note_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_session_note(db: AsyncSession, note_id: str, note_in: SessionNoteUpdate) -> SessionNote | None:
    db_obj = await get_session_note(db, note_id)
    if not db_obj:
        return None
    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj