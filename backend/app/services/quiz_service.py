"""Quiz service — handles quiz session logic."""

import uuid
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question, AnswerOption
from app.models.progress import UserProgress


# In-memory storage for quiz sessions (MVP approach)
# Stores session_id -> { question_order -> { question_id, selected_option_ids } }
quiz_sessions: Dict[str, dict] = {}


async def create_quiz_session(db: AsyncSession) -> str:
    """Create a new quiz session and return its ID."""
    session_id = str(uuid.uuid4())
    quiz_sessions[session_id] = {
        "current_question_order": 0,
        "answers": {},  # question_id -> [option_ids]
    }
    return session_id


async def get_first_question(db: AsyncSession):
    """Get the first question ordered by 'order' field."""
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.options))
        .order_by(Question.order)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_question_by_order(db: AsyncSession, order: int):
    """Get a question by its order position."""
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.order == order)
    )
    return result.scalar_one_or_none()



async def save_answer(session_id: str, question_id: int, option_ids: List[int]):
    """Save user's answer for a question in the session."""
    if session_id not in quiz_sessions:
        return False

    quiz_sessions[session_id]["answers"][question_id] = option_ids
    quiz_sessions[session_id]["current_question_order"] += 1
    return True


async def get_next_question(db: AsyncSession, session_id: str):
    """Get the next question for the session."""
    if session_id not in quiz_sessions:
        return None

    next_order = quiz_sessions[session_id]["current_question_order"]
    question = await get_question_by_order(db, next_order)
    return question


async def is_quiz_finished(db: AsyncSession, session_id: str) -> bool:
    """Check if all questions have been answered."""
    if session_id not in quiz_sessions:
        return True

    # Count total questions
    result = await db.execute(select(Question))
    total_questions = len(result.scalars().all())

    next_order = quiz_sessions[session_id]["current_question_order"]
    return next_order >= total_questions


def get_session_answers(session_id: str) -> Dict[int, List[int]]:
    """Get all answers for a session: question_id -> [option_ids]."""
    if session_id not in quiz_sessions:
        return {}
    return quiz_sessions[session_id]["answers"]


async def finish_quiz(db: AsyncSession, session_id: str):
    """Mark quiz as finished for the session."""
    if session_id not in quiz_sessions:
        return False

    # Create user_progress record
    result = await db.execute(
        select(UserProgress).where(UserProgress.session_id == session_id)
    )
    up = result.scalar_one_or_none()

    if up:
        up.finished_quiz = True
        await db.commit()

    return True


async def ensure_user_progress(db: AsyncSession, session_id: str, profession_id: str):
    """Ensure UserProgress record exists."""
    result = await db.execute(
        select(UserProgress).where(UserProgress.session_id == session_id)
    )
    up = result.scalar_one_or_none()
    if not up:
        up = UserProgress(
            session_id=session_id,
            profession_id=profession_id,
            finished_quiz=False,
        )
        db.add(up)
        await db.commit()
    return up
