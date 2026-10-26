from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.crud import progress_record as crud
from app.schemas.progress_record import ProgressRecordCreate, ProgressRecordOut

router = APIRouter()


@router.post("/", response_model=ProgressRecordOut)
async def create_progress_record(record_in: ProgressRecordCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_progress_record(db, record_in, student_id=record_in.student_id)


@router.get("/", response_model=List[ProgressRecordOut])
async def list_progress_records(
    student_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    if student_id:
        return await crud.get_progress_records_by_student(db, student_id, skip=skip, limit=limit)
    return await crud.get_all_progress_records(db, skip=skip, limit=limit)