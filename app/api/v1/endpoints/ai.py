from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai_service import generate_study_plan_topics, get_live_pedagogical_copilot

router = APIRouter()


class GenerateTopicsRequest(BaseModel):
    subject: str
    level: Optional[str] = "Upper Sixth / Secondary"
    goal: str
    total_minutes: Optional[int] = 60
    student_notes: Optional[str] = None


class TopicItem(BaseModel):
    title: str
    order_index: int
    planned_minutes: int
    key_concept: Optional[str] = None
    socratic_question: Optional[str] = None
    common_stumbling_block: Optional[str] = None


class GenerateTopicsResponse(BaseModel):
    title: str
    summary: Optional[str] = None
    topics: List[TopicItem]
    model_used: Optional[str] = None


class CopilotAdviceRequest(BaseModel):
    topic_title: str
    student_struggle: str
    elapsed_minutes: Optional[int] = None
    subject: Optional[str] = None


class CopilotAdviceResponse(BaseModel):
    advice: str
    model_used: Optional[str] = None


@router.post("/generate-topics", response_model=GenerateTopicsResponse)
async def generate_topics_endpoint(payload: GenerateTopicsRequest):
    try:
        data = await generate_study_plan_topics(
            subject=payload.subject,
            level=payload.level or "Secondary",
            concept_or_goal=payload.goal,
            total_minutes=payload.total_minutes or 60,
            student_notes=payload.student_notes,
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic generation failed: {str(e)}")


@router.post("/copilot-hint", response_model=CopilotAdviceResponse)
async def copilot_hint_endpoint(payload: CopilotAdviceRequest):
    try:
        data = await get_live_pedagogical_copilot(
            topic_title=payload.topic_title,
            student_struggle=payload.student_struggle,
            elapsed_minutes=payload.elapsed_minutes,
            subject=payload.subject,
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot hint failed: {str(e)}")

