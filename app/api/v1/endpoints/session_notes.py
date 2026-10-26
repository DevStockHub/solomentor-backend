from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.crud import session_note as crud
from app.schemas.session_note import SessionNoteCreate, SessionNoteUpdate, SessionNoteOut

router = APIRouter()


@router.post("/", response_model=SessionNoteOut)
async def create_session_note(note_in: SessionNoteCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_session_note(db, note_in)


@router.get("/", response_model=List[SessionNoteOut])
async def list_session_notes(plan_id: str, db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    return await crud.get_session_notes_by_plan(db, plan_id, skip=skip, limit=limit)


@router.put("/{note_id}", response_model=SessionNoteOut)
async def update_session_note(note_id: str, note_in: SessionNoteUpdate, db: AsyncSession = Depends(get_db)):
    note = await crud.update_session_note(db, note_id, note_in)
    if not note:
        raise HTTPException(status_code=404, detail="Session note not found")
    return note