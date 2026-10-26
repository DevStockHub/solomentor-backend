from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.crud.chat_message import (
    create_chat_message,
    get_chat_messages,
    get_chat_sessions,
    get_chat_session_by_id,
    create_chat_session,
    delete_chat_session,
    update_chat_session_title,
)
from app.schemas.chat_message import (
    ChatMessageCreate,
    ChatMessageOut,
    ChatRequest,
    ChatResponse,
    ChatSessionOut,
    ChatSessionCreate,
    ChatSessionDetail,
)
from app.models.mentor_profile import MentorProfile
from app.models.student import Student
from app.models.subject import Subject
from app.models.session_plan import SessionPlan
from app.models.topic import Topic
from app.models.progress_record import ProgressRecord
from app.services.ai_service import call_openrouter_with_fallback

router = APIRouter()


async def build_full_app_context(db: AsyncSession) -> str:
    """
    Assembles real-time knowledge of all students, subjects, active session plans,
    topics, and recorded learning stumbles across the entire app.
    """
    # 1. Mentor Profile
    mentor_res = await db.execute(select(MentorProfile).limit(1))
    mentor = mentor_res.scalar_one_or_none()
    mentor_str = (
        f"Mentor: {mentor.name or 'Solo Mentor'} | Subjects: {mentor.subjects or 'STEM'}\n"
        f"Philosophy: {mentor.bio or 'Intuitive understanding, Socratic inquiry, problem-solving mastery.'}"
        if mentor
        else "Mentor: STEM Secondary Mentor"
    )

    # 2. Students
    students_res = await db.execute(select(Student).order_by(Student.name.asc()))
    students = list(students_res.scalars().all())
    student_map = {s.id: s.name for s in students}
    
    students_lines = []
    if students:
        for s in students:
            info = f"- {s.name} ({s.grade or 'Secondary'}, {s.school or 'School'})"
            if s.notes:
                info += f" | Diagnostic: {s.notes}"
            students_lines.append(info)
    else:
        students_lines.append("- No students registered yet.")

    # 3. Session Plans & Topics
    plans_res = await db.execute(
        select(SessionPlan).order_by(desc(SessionPlan.created_at)).limit(10)
    )
    plans = list(plans_res.scalars().all())
    
    plans_lines = []
    if plans:
        for p in plans:
            # Load topics
            topics_res = await db.execute(
                select(Topic).where(Topic.session_plan_id == p.id).order_by(Topic.order_index.asc())
            )
            topics = list(topics_res.scalars().all())
            topics_desc = ", ".join([f"{t.title} ({t.status})" for t in topics]) if topics else "No subtopics"
            st_name = student_map.get(p.student_id, "Unknown Student")
            plans_lines.append(
                f"- Plan: \"{p.title}\" | Mentee: {st_name} | Status: {p.status} | Target: {p.planned_minutes}m | Topics: [{topics_desc}]"
            )
    else:
        plans_lines.append("- No session plans created yet.")

    # 4. Progress Records & Stumbles
    records_res = await db.execute(
        select(ProgressRecord).order_by(desc(ProgressRecord.created_at)).limit(15)
    )
    records = list(records_res.scalars().all())
    
    stumbles_lines = []
    if records:
        for r in records:
            st_name = student_map.get(r.student_id, "Student")
            details = []
            if r.struggle_noted:
                details.append(f"Struggle: {r.struggle_noted}")
            if r.approach_used:
                details.append(f"Approach: {r.approach_used}")
            if r.outcome:
                details.append(f"Outcome: {r.outcome}")
            if r.effectiveness_rating:
                details.append(f"Rating: {r.effectiveness_rating}/5")
            stumbles_lines.append(f"- Mentee: {st_name} | " + " • ".join(details))
    else:
        stumbles_lines.append("- No historical struggle logs recorded yet.")

    # 5. Subjects
    subjects_res = await db.execute(select(Subject).order_by(Subject.name.asc()))
    subjects = list(subjects_res.scalars().all())
    subjects_str = ", ".join([s.name for s in subjects]) if subjects else "Mathematics, Physics, Computer Science, ICT, Chemistry"

    context_prompt = (
        "=== SOLO MENTOR APP REAL-TIME KNOWLEDGE BASE ===\n"
        f"{mentor_str}\n\n"
        f"Available Subjects: {subjects_str}\n\n"
        "--- ENROLLED SECONDARY STUDENTS ---\n"
        + "\n".join(students_lines)
        + "\n\n--- RECENT SESSION PLANS & TOPICS ---\n"
        + "\n".join(plans_lines)
        + "\n\n--- RECORDED STUMBLES & PEDAGOGICAL BREAKTHROUGHS ---\n"
        + "\n".join(stumbles_lines)
        + "\n==============================================="
    )
    return context_prompt


# --- Session Management Endpoints ---

@router.get("/sessions", response_model=List[ChatSessionOut])
async def list_chat_sessions(db: AsyncSession = Depends(get_db)):
    """List all chat sessions with message counts and last message snippet."""
    return await get_chat_sessions(db)


@router.post("/sessions", response_model=ChatSessionOut)
async def create_new_chat_session(
    payload: Optional[ChatSessionCreate] = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversational thread."""
    title = payload.title if payload and payload.title else "New Chat"
    session = await create_chat_session(db, title=title)
    return ChatSessionOut(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,
        last_message=None,
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
async def get_session_details(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get chat session and its full message history."""
    session = await get_chat_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = await get_chat_messages(db, session_id=session_id)
    return ChatSessionDetail(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(messages),
        last_message=messages[-1].content if messages else None,
        messages=[ChatMessageOut.model_validate(m) for m in messages],
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a chat session and all its messages."""
    deleted = await delete_chat_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"status": "success", "deleted_session_id": session_id}


# --- Chat Interaction Endpoint ---

@router.post("/", response_model=ChatResponse)
async def chat_message(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Send a message in a chat session or session plan.
    Injects real-time application data (students, plans, struggles, subjects) into the prompt.
    """
    session_id = request.session_id
    plan_id = request.session_plan_id

    # If no session_id and no plan_id provided, create a default ChatSession
    if not session_id and not plan_id:
        new_session = await create_chat_session(db, title="New Chat")
        session_id = new_session.id

    # Save user message
    user_msg = ChatMessageCreate(role="mentor", content=request.message)
    await create_chat_message(db, user_msg, session_id=session_id, plan_id=plan_id)

    # Fetch live app knowledge
    app_context = await build_full_app_context(db)

    system_prompt = (
        "You are the SoloMentor AI Pedagogical Copilot & Curriculum Strategist for a mentor "
        "teaching secondary school (O-Level / Form 4 & 5) and sixth-form (Lower & Upper Sixth) students. "
        "You help with Mathematics, Physics, Computer Science, and ICT.\n\n"
        "Here is the LIVE DATA from the mentor's app:\n"
        f"{app_context}\n\n"
        "GUIDELINES:\n"
        "1. Deeply leverage the live student roster, diagnostic goals, and past struggles when giving advice.\n"
        "2. Provide intuitive physical/visual analogies, Socratic diagnostic questions, and pacing tips.\n"
        "3. Keep formulas clean and human-readable without raw unrendered LaTeX markers like \\frac or \\times.\n"
        "4. Be direct, pedagogical, practical, and highly encouraging."
    )

    messages = [{"role": "system", "content": system_prompt}]

    # Load history
    history = await get_chat_messages(db, session_id=session_id, plan_id=plan_id, limit=16)
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    try:
        ai_response, model_used = await call_openrouter_with_fallback(messages)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat error: {str(e)}")

    # Save AI response
    ai_msg = ChatMessageCreate(role="ai", content=ai_response)
    await create_chat_message(db, ai_msg, session_id=session_id, plan_id=plan_id)

    # Auto-generate a title if session has default "New Chat" title
    updated_title = None
    if session_id:
        sess = await get_chat_session_by_id(db, session_id)
        if sess and (sess.title == "New Chat" or not sess.title):
            # Derive clean title from first prompt (max 30 chars)
            first_prompt_title = request.message.strip().replace("\n", " ")
            if len(first_prompt_title) > 32:
                first_prompt_title = first_prompt_title[:32] + "..."
            sess.title = first_prompt_title
            await db.commit()
            updated_title = sess.title
        elif sess:
            updated_title = sess.title

    return ChatResponse(
        response=ai_response,
        model_used=model_used,
        session_id=session_id,
        session_title=updated_title,
    )


# Backward-compatible endpoint for plan-specific chat history
@router.get("/{plan_id}", response_model=List[ChatMessageOut])
async def get_plan_chat_history(plan_id: str, db: AsyncSession = Depends(get_db)):
    messages = await get_chat_messages(db, plan_id=plan_id)
    return [ChatMessageOut.model_validate(m) for m in messages]
