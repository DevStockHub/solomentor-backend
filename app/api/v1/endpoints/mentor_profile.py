from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.crud import mentor_profile as crud
from app.schemas.mentor_profile import MentorProfileCreate, MentorProfileUpdate, MentorProfileOut

router = APIRouter()


@router.post("/", response_model=MentorProfileOut)
async def create_profile(profile_in: MentorProfileCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_mentor_profile_by_name(db, profile_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Profile with this name already exists")
    return await crud.create_mentor_profile(db, profile_in)


@router.get("/", response_model=MentorProfileOut)
async def get_profile(db: AsyncSession = Depends(get_db)):
    profile = await crud.get_first_mentor_profile(db)
    if not profile:
        raise HTTPException(status_code=404, detail="No mentor profile found")
    return profile


@router.put("/{profile_id}", response_model=MentorProfileOut)
async def update_profile(profile_id: str, profile_in: MentorProfileUpdate, db: AsyncSession = Depends(get_db)):
    profile = await crud.update_mentor_profile(db, profile_id, profile_in)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile