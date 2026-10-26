from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.crud import subject as crud
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectOut

router = APIRouter()


@router.post("/", response_model=SubjectOut)
async def create_subject(subject_in: SubjectCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_subject(db, subject_in)


@router.get("/", response_model=List[SubjectOut])
async def list_subjects(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    return await crud.get_subjects(db, skip=skip, limit=limit)


@router.get("/{subject_id}", response_model=SubjectOut)
async def get_subject(subject_id: str, db: AsyncSession = Depends(get_db)):
    subject = await crud.get_subject(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.put("/{subject_id}", response_model=SubjectOut)
async def update_subject(subject_id: str, subject_in: SubjectUpdate, db: AsyncSession = Depends(get_db)):
    subject = await crud.update_subject(db, subject_id, subject_in)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject