"""Quiz service — handles quiz session logic with database persistence."""

import json
import uuid
from typing import Dict, List

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question, AnswerOption
from app.models.progress import UserProgress
from app.models.quiz_session import QuizSession


async def create_quiz_session(db: AsyncSession) -> str:
    """Create a new quiz session and return its ID."""
    session_id = str(uuid.uuid4())
    session = QuizSession(
        session_id=session_id,
        current_question_order=0,
        answers_json="{}",
        finished=False,
    )
    db.add(session)
    await db.commit()
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


async def save_answer(db: AsyncSession, session_id: str, question_id: int, option_ids: List[int]):
    """Save user's answer for a question in the session."""
    result = await db.execute(
        select(QuizSession).where(QuizSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return False

    answers = json.loads(session.answers_json) if session.answers_json else {}
    answers[str(question_id)] = option_ids
    session.answers_json = json.dumps(answers)
    session.current_question_order += 1
    await db.commit()
    return True


async def get_next_question(db: AsyncSession, session_id: str):
    """Get the next question for the session."""
    result = await db.execute(
        select(QuizSession).where(QuizSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return None

    next_order = session.current_question_order
    question = await get_question_by_order(db, next_order)
    return question


async def is_quiz_finished(db: AsyncSession, session_id: str) -> bool:
    """Check if all questions have been answered."""
    result = await db.execute(
        select(QuizSession).where(QuizSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return True

    # Count total questions
    count_result = await db.execute(select(func.count()).select_from(Question))
    total_questions = count_result.scalar()

    return session.current_question_order >= total_questions


async def get_session_answers(db: AsyncSession, session_id: str) -> Dict[int, List[int]]:
    """Get all answers for a session: question_id -> [option_ids]."""
    result = await db.execute(
        select(QuizSession).where(QuizSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session or not session.answers_json:
        return {}

    raw = json.loads(session.answers_json)
    return {int(k): v for k, v in raw.items()}


async def finish_quiz(db: AsyncSession, session_id: str):
    """Mark quiz as finished for the session."""
    result = await db.execute(
        select(QuizSession).where(QuizSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return False

    session.finished = True

    # Create user_progress record
    up_result = await db.execute(
        select(UserProgress).where(UserProgress.session_id == session_id)
    )
    up = up_result.scalar_one_or_none()
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


async def link_session_to_user(db: AsyncSession, session_id: str, user_id: int):
    """Link an existing quiz session to a registered user."""
    result = await db.execute(
        select(QuizSession).where(QuizSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if session:
        session.user_id = user_id
        await db.commit()
        return True
    return False

