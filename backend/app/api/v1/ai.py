"""AI coach API endpoints with grounded RAG and streaming responses."""
import json
from datetime import datetime, timezone, date, timedelta
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.ai import Conversation, ConversationMessage, AIInsight
from app.models.user import UserProfile
from app.models.activity import Activity
from app.models.health import DailyHealthMetric, SleepRecord
from app.models.training import RaceGoal
from app.models.base import new_uuid
from app.providers.llm import get_llm_provider
from app.ai.system_prompt import COACH_SYSTEM_PROMPT
from app.ai.context_builder import build_full_context
from app.ai.coach import TrainingCoach
from app.analytics.running import ActivityRow
from app.analytics.health import HealthRow, SleepRow

router = APIRouter()


async def _user(db: AsyncSession) -> UserProfile:
    r = await db.execute(select(UserProfile).limit(1))
    user = r.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User profile not initialized")
    return user


class MessageCreate(BaseModel):
    content: str


class ConversationCreate(BaseModel):
    title: str = "New Training Consultation"


@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    r = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(desc(Conversation.updated_at))
    )
    convs = r.scalars().all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
        }
        for c in convs
    ]


@router.post("/conversations")
async def create_conversation(req: ConversationCreate, db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    conv = Conversation(id=new_uuid(), user_id=user.id, title=req.title)
    db.add(conv)
    await db.commit()
    return {"id": conv.id, "title": conv.title, "created_at": conv.created_at.isoformat()}


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    conv_r = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    if not conv_r.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    r = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at)
    )
    messages = r.scalars().all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str, req: MessageCreate, db: AsyncSession = Depends(get_db)
):
    user = await _user(db)
    conv_r = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    conv = conv_r.scalar_one_or_none()
    if not conv:
        # Create conversation automatically if not exists
        conv = Conversation(id=conversation_id, user_id=user.id, title=req.content[:30])
        db.add(conv)
        await db.commit()

    # 1. Save user message
    user_msg = ConversationMessage(
        id=new_uuid(),
        conversation_id=conversation_id,
        role="user",
        content=req.content,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user_msg)
    await db.commit()

    # 2. Build structured DB context (grounded retrieval)
    grounded_context = await build_full_context(db, user.id)

    # 3. Retrieve recent conversation history
    hist_r = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at)
        .limit(10)
    )
    history = hist_r.scalars().all()

    llm_messages = [
        {"role": "system", "content": f"{COACH_SYSTEM_PROMPT}\n\n### USER'S CURRENT MEASURED DATA:\n{grounded_context}"}
    ]
    for m in history:
        llm_messages.append({"role": m.role, "content": m.content})

    # 4. Stream response from provider
    llm = get_llm_provider()

    async def event_generator() -> AsyncGenerator[str, None]:
        full_response_chunks = []
        try:
            stream_or_str = await llm.chat(llm_messages, stream=True)
            if isinstance(stream_or_str, str):
                yield f"data: {stream_or_str}\n\n"
                full_response_chunks.append(stream_or_str)
            else:
                async for chunk in stream_or_str:
                    yield f"data: {chunk}\n\n"
                    full_response_chunks.append(chunk)
            yield "data: [DONE]\n\n"
        except Exception as exc:
            err_text = f"Coaching service unavailable: {str(exc)}"
            yield f"data: {err_text}\n\n"
            yield "data: [DONE]\n\n"
            full_response_chunks.append(err_text)
        finally:
            # Store assistant response back into DB
            assistant_content = "".join(full_response_chunks)
            if assistant_content:
                assistant_msg = ConversationMessage(
                    id=new_uuid(),
                    conversation_id=conversation_id,
                    role="assistant",
                    content=assistant_content,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(assistant_msg)
                await db.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/recommendations")
async def get_recommendations(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    coach = TrainingCoach()

    # Load activities
    cutoff_act = date.today() - timedelta(days=60)
    act_r = await db.execute(
        select(Activity).where(and_(Activity.user_id == user.id, Activity.start_time >= cutoff_act))
    )
    act_rows = [
        ActivityRow(
            start_time_date=a.start_time.date(),
            duration_seconds=a.duration_seconds,
            distance_meters=a.distance_meters,
            avg_speed_ms=a.avg_speed_ms,
            avg_heart_rate=a.avg_heart_rate,
            max_heart_rate=a.max_heart_rate,
            avg_cadence=a.avg_cadence,
            elevation_gain=a.elevation_gain,
            sport_type=a.sport_type,
            calories=a.calories,
        )
        for a in act_r.scalars().all()
    ]

    # Load health
    cutoff_health = date.today() - timedelta(days=14)
    h_r = await db.execute(
        select(DailyHealthMetric).where(
            and_(DailyHealthMetric.user_id == user.id, DailyHealthMetric.calendar_date >= cutoff_health)
        )
    )
    health_rows = [
        HealthRow(
            calendar_date=h.calendar_date,
            resting_heart_rate=h.resting_heart_rate,
            avg_stress_level=h.avg_stress_level,
            body_battery_high=h.body_battery_high,
            body_battery_low=h.body_battery_low,
            steps=h.steps,
        )
        for h in h_r.scalars().all()
    ]

    # Load sleep
    s_r = await db.execute(
        select(SleepRecord).where(
            and_(SleepRecord.user_id == user.id, SleepRecord.calendar_date >= cutoff_health)
        )
    )
    sleep_rows = [
        SleepRow(
            calendar_date=s.calendar_date,
            total_sleep_seconds=s.total_sleep_seconds,
            deep_sleep_seconds=s.deep_sleep_seconds,
            rem_sleep_seconds=s.rem_sleep_seconds,
            sleep_score=s.sleep_score,
            hrv_last_night=s.hrv_last_night,
            hrv_weekly_avg=s.hrv_weekly_avg,
        )
        for s in s_r.scalars().all()
    ]

    # Race goal
    g_r = await db.execute(
        select(RaceGoal).where(and_(RaceGoal.user_id == user.id, RaceGoal.status == "active")).limit(1)
    )
    goal = g_r.scalar_one_or_none()
    goal_dict = None
    if goal:
        goal_dict = {
            "name": goal.race_name,
            "target_date": goal.race_date.isoformat() if goal.race_date else None,
            "distance_meters": goal.distance_meters,
        }

    recs = coach.analyze(act_rows, health_rows, sleep_rows, goal_dict)
    return [
        {
            "category": r.category,
            "title": r.title,
            "rationale": r.rationale,
            "action": r.action,
            "confidence": r.confidence,
            "caveat": r.caveat,
        }
        for r in recs
    ]


@router.get("/briefing")
async def get_daily_briefing(db: AsyncSession = Depends(get_db)):
    user = await _user(db)
    # Check latest sleep
    today = date.today()
    yesterday = today - timedelta(days=1)
    s_r = await db.execute(
        select(SleepRecord)
        .where(and_(SleepRecord.user_id == user.id, SleepRecord.calendar_date >= yesterday))
        .order_by(desc(SleepRecord.calendar_date))
        .limit(1)
    )
    sleep = s_r.scalar_one_or_none()

    # Get recent mileage
    monday = today - timedelta(days=today.weekday())
    act_r = await db.execute(
        select(Activity).where(and_(Activity.user_id == user.id, Activity.start_time >= monday))
    )
    week_acts = act_r.scalars().all()
    week_km = sum(a.distance_meters or 0 for a in week_acts if a.sport_type == "running") / 1000

    sleep_summary = (
        f"Sleep score {sleep.sleep_score}/100 with overnight HRV of {sleep.hrv_last_night}ms."
        if sleep and sleep.sleep_score
        else "No overnight sleep data recorded yet."
    )

    briefing = (
        f"Good morning! You've logged {week_km:.1f} km of running across {len(week_acts)} workouts this week. "
        f"{sleep_summary} "
        f"Based on your current recovery trends, focus on keeping your effort controlled today."
    )

    return {
        "date": today.isoformat(),
        "summary": briefing,
        "weekly_km": round(week_km, 1),
        "sleep_score": sleep.sleep_score if sleep else None,
        "hrv": sleep.hrv_last_night if sleep else None,
    }
