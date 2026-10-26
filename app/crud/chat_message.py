from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.schemas.chat_message import ChatMessageCreate


# --- ChatSession CRUD ---

async def get_chat_sessions(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[dict]:
    result = await db.execute(
        select(ChatSession).order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit)
    )
    sessions = list(result.scalars().all())

    session_list = []
    for s in sessions:
        # Get count and latest message preview
        msg_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == s.id)
            .order_by(desc(ChatMessage.created_at))
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()
        
        count_res = await db.execute(
            select(func.count(ChatMessage.id)).where(ChatMessage.session_id == s.id)
        )
        msg_count = count_res.scalar() or 0

        session_list.append({
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "message_count": msg_count,
            "last_message": (last_msg.content[:80] + "...") if last_msg and len(last_msg.content) > 80 else (last_msg.content if last_msg else None),
        })
    return session_list


async def get_chat_session_by_id(db: AsyncSession, session_id: str) -> Optional[ChatSession]:
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    return result.scalar_one_or_none()


async def create_chat_session(db: AsyncSession, title: str = "New Chat") -> ChatSession:
    session = ChatSession(title=title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def update_chat_session_title(db: AsyncSession, session_id: str, title: str) -> Optional[ChatSession]:
    session = await get_chat_session_by_id(db, session_id)
    if session:
        session.title = title
        await db.commit()
        await db.refresh(session)
    return session


async def delete_chat_session(db: AsyncSession, session_id: str) -> bool:
    session = await get_chat_session_by_id(db, session_id)
    if not session:
        return False
    await db.delete(session)
    await db.commit()
    return True


# --- ChatMessage CRUD ---

async def get_chat_messages(
    db: AsyncSession,
    session_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    limit: int = 100,
) -> List[ChatMessage]:
    query = select(ChatMessage).order_by(ChatMessage.created_at.asc()).limit(limit)
    if session_id:
        query = query.where(ChatMessage.session_id == session_id)
    elif plan_id:
        query = query.where(ChatMessage.session_plan_id == plan_id)
    else:
        return []

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_chat_messages_by_plan(
    db: AsyncSession, plan_id: str, skip: int = 0, limit: int = 100
) -> List[ChatMessage]:
    return await get_chat_messages(db, plan_id=plan_id, limit=limit)


async def create_chat_message(
    db: AsyncSession,
    message_in: ChatMessageCreate,
    session_id: Optional[str] = None,
    plan_id: Optional[str] = None,
) -> ChatMessage:
    db_obj = ChatMessage(
        **message_in.model_dump(),
        session_id=session_id,
        session_plan_id=plan_id,
    )
    db.add(db_obj)
    
    # Touch session updated_at
    if session_id:
        session = await get_chat_session_by_id(db, session_id)
        if session:
            session.updated_at = func.now()

    await db.commit()
    await db.refresh(db_obj)
    return db_obj
