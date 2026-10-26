from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.subject import Subject
from app.api.v1.endpoints import (
    mentor_profile,
    students,
    subjects,
    session_plans,
    topics,
    session_notes,
    progress,
    chat,
    ai,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed default STEM subjects if not already seeded
    default_subjects = [
        {"name": "Mathematics", "code": "MATH", "description": "Pure Mathematics, Calculus, Algebra & Statistics"},
        {"name": "Physics", "code": "PHY", "description": "Mechanics, Electromagnetism, Waves & Modern Physics"},
        {"name": "Computer Science", "code": "CS", "description": "Algorithms, Data Structures & Programming"},
        {"name": "ICT", "code": "ICT", "description": "Information and Communications Technology"},
        {"name": "Chemistry", "code": "CHEM", "description": "Physical, Inorganic & Organic Chemistry"},
        {"name": "Further Mathematics", "code": "FMATH", "description": "Advanced Mechanics, Complex Numbers & Matrices"},
    ]

    async with AsyncSessionLocal() as session:
        for item in default_subjects:
            res = await session.execute(select(Subject).where(Subject.name == item["name"]))
            existing = res.scalar_one_or_none()
            if not existing:
                sub = Subject(name=item["name"], code=item["code"], description=item["description"])
                session.add(sub)
        await session.commit()

    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Add CORS Middleware for mobile apps & web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mentor_profile.router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(subjects.router, prefix="/api/v1/subjects", tags=["subjects"])
app.include_router(session_plans.router, prefix="/api/v1/session-plans", tags=["session-plans"])
app.include_router(topics.router, prefix="/api/v1/topics", tags=["topics"])
app.include_router(session_notes.router, prefix="/api/v1/session-notes", tags=["session-notes"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])


@app.get("/")
async def root():
    return {"message": "SoloMentor Backend is running", "app": settings.APP_NAME}


@app.get("/health")
async def health():
    return {"status": "healthy"}
