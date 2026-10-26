from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.crud import student as crud
from app.crud import mentor_profile as mentor_crud
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut

router = APIRouter()


@router.post("/", response_model=StudentOut)
async def create_student(student_in: StudentCreate, db: AsyncSession = Depends(get_db)):
    mentor_id = student_in.mentor_id
    if not mentor_id:
        mentor = await mentor_crud.get_first_mentor_profile(db)
        if not mentor:
            # Create a default profile if none exists
            from app.schemas.mentor_profile import MentorProfileCreate
            mentor = await mentor_crud.create_mentor_profile(
                db, MentorProfileCreate(name="Solo Mentor", subjects="MATH,PHY,CS,ICT")
            )
        mentor_id = mentor.id

    return await crud.create_student(db, student_in, mentor_id=mentor_id)


@router.get("/", response_model=List[StudentOut])
async def list_students(
    mentor_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    if mentor_id:
        return await crud.get_students_by_mentor(db, mentor_id, skip=skip, limit=limit)
    return await crud.get_all_students(db, skip=skip, limit=limit)


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(student_id: str, db: AsyncSession = Depends(get_db)):
    student = await crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentOut)
async def update_student(student_id: str, student_in: StudentUpdate, db: AsyncSession = Depends(get_db)):
    student = await crud.update_student(db, student_id, student_in)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.delete("/{student_id}")
async def delete_student(student_id: str, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted"}