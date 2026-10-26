from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.crud import session_plan as crud
from app.schemas.session_plan import SessionPlanCreate, SessionPlanUpdate, SessionPlanOut

router = APIRouter()


@router.post("/", response_model=SessionPlanOut)
async def create_session_plan(plan_in: SessionPlanCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_session_plan(db, plan_in)


@router.get("/", response_model=List[SessionPlanOut])
async def list_session_plans(
    student_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    if student_id:
        return await crud.get_session_plans_by_student(db, student_id, skip=skip, limit=limit)
    return await crud.get_all_session_plans(db, skip=skip, limit=limit)


@router.get("/{plan_id}", response_model=SessionPlanOut)
async def get_session_plan(plan_id: str, db: AsyncSession = Depends(get_db)):
    plan = await crud.get_session_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Session plan not found")
    return plan


@router.put("/{plan_id}", response_model=SessionPlanOut)
async def update_session_plan(plan_id: str, plan_in: SessionPlanUpdate, db: AsyncSession = Depends(get_db)):
    plan = await crud.update_session_plan(db, plan_id, plan_in)
    if not plan:
        raise HTTPException(status_code=404, detail="Session plan not found")
    return plan


@router.delete("/{plan_id}")
async def delete_session_plan(plan_id: str, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_session_plan(db, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session plan not found")
    return {"message": "Session plan deleted"}