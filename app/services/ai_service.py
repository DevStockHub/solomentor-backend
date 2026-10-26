import json
import re
from typing import List, Dict, Any, Tuple, Optional
import httpx
from fastapi import HTTPException

from app.core.config import settings


def sanitize_messages_for_llm(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Map internal roles ('mentor' -> 'user', 'ai' -> 'assistant') for OpenRouter / OpenAI API."""
    sanitized = []
    for msg in messages:
        role = msg.get("role", "user")
        if role == "mentor":
            clean_role = "user"
        elif role in ("ai", "assistant"):
            clean_role = "assistant"
        elif role == "system":
            clean_role = "system"
        else:
            clean_role = "user"
        sanitized.append({"role": clean_role, "content": msg.get("content", "")})
    return sanitized


async def call_openrouter_with_fallback(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 1200,
) -> Tuple[str, str]:
    """Call OpenRouter with configured primary model, falling back to secondary models."""
    clean_messages = sanitize_messages_for_llm(messages)
    models = [settings.AI_PRIMARY_MODEL] + settings.get_secondary_models()
    last_error = None

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://solomentor.local",
        "X-Title": "SoloMentor",
    }

    async with httpx.AsyncClient(timeout=35.0) as client:
        for model in models:
            try:
                response = await client.post(
                    f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json={
                        "model": model,
                        "messages": clean_messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return content, model
                else:
                    last_error = f"Model {model} returned status {response.status_code}: {response.text[:120]}"
            except Exception as e:
                last_error = f"Model {model} error: {str(e)}"
                continue

    raise HTTPException(
        status_code=503,
        detail=f"All configured AI models failed. Last error: {last_error}",
    )


def extract_json_from_text(text: str) -> Any:
    """Extract and parse JSON object or array from markdown or raw text."""
    # Try direct parse
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting markdown json code block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding first [ or { to last ] or }
    start_bracket = text.find("[")
    end_bracket = text.rfind("]")
    if start_bracket != -1 and end_bracket > start_bracket:
        try:
            return json.loads(text[start_bracket : end_bracket + 1])
        except json.JSONDecodeError:
            pass

    start_brace = text.find("{")
    end_brace = text.rfind("}")
    if start_brace != -1 and end_brace > start_brace:
        try:
            return json.loads(text[start_brace : end_brace + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse valid JSON from AI response: {text[:200]}")


async def generate_study_plan_topics(
    subject: str,
    level: str,
    concept_or_goal: str,
    total_minutes: int = 60,
    student_notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate structured study topics for a session plan using pedagogical STEM guidelines."""
    system_prompt = (
        "You are an expert STEM pedagogical mentor for secondary school and sixth-form students. "
        "Your task is to break down a study goal into an intentional, highly focused 1-on-1 mentoring session plan. "
        "Return ONLY a valid JSON object with no preamble or wrapping other than json."
    )

    user_prompt = f"""Break down the following mentoring goal into a realistic, structured session plan:
Subject: {subject}
Student Level: {level or 'Secondary / Sixth-Form'}
Session Goal / Topic: {concept_or_goal}
Target Total Duration: {total_minutes} minutes
{f'Student Background/Struggles: {student_notes}' if student_notes else ''}

Return a JSON object matching this exact schema:
{{
  "title": "A concise, engaging title for the session",
  "summary": "1-2 sentence pedagogical objective for this session",
  "topics": [
    {{
      "title": "Subtopic title (e.g. Intuitive Foundation, Core Derivation, Guided Problem Solving, Edge Cases & Misconceptions)",
      "order_index": 1,
      "planned_minutes": 15,
      "key_concept": "Brief explanation of what the student must grasp here",
      "socratic_question": "One insightful question the mentor should ask to test understanding",
      "common_stumbling_block": "The most frequent error or confusion secondary students make here"
    }}
  ]
}}

Ensure:
1. Total planned_minutes across topics approximately equals {total_minutes} minutes.
2. 3 to 5 bite-sized, sequential topics.
3. Realistic time estimates for deep comprehension and active dialogue (not lecturing).
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    raw_response, model_used = await call_openrouter_with_fallback(
        messages, temperature=0.5, max_tokens=1500
    )
    parsed = extract_json_from_text(raw_response)
    if isinstance(parsed, list):
        parsed = {"title": concept_or_goal, "summary": "", "topics": parsed}
    parsed["model_used"] = model_used
    return parsed


async def get_live_pedagogical_copilot(
    topic_title: str,
    student_struggle: str,
    elapsed_minutes: Optional[int] = None,
    subject: Optional[str] = None,
) -> Dict[str, Any]:
    """Provide real-time tactical mentoring advice when a student is stuck."""
    system_prompt = (
        "You are an empathetic, sharp STEM mentor coach. "
        "A mentor is currently mid-session with a secondary school student who is struggling. "
        "Provide direct, high-leverage pedagogical interventions. Be concise and practical."
    )

    user_prompt = f"""The mentor is working on:
Topic: {topic_title}
{f'Subject: {subject}' if subject else ''}
{f'Elapsed Time on topic: {elapsed_minutes} minutes' if elapsed_minutes else ''}
Student's Current Struggle / Confusion: {student_struggle}

Respond in concise, actionable advice:
1. Intuitive Analogy / Real-world visual
2. The Micro-Step (how to break this into a simpler 30-second sub-problem)
3. Socratic Prompt (the exact question the mentor should ask the student right now)
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response_text, model_used = await call_openrouter_with_fallback(
        messages, temperature=0.6, max_tokens=600
    )
    return {"advice": response_text, "model_used": model_used}

