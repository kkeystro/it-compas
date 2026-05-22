from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.question import Question
from app.schemas.quiz import (
    QuizStartOut,
    QuizAnswerIn,
    QuizAnswerOut,
    QuestionOut,
    AnswerOptionOut,
)
from app.services.quiz_service import (
    create_quiz_session,
    get_first_question,
    get_next_question,
    save_answer,
    is_quiz_finished,
    ensure_user_progress,
    finish_quiz as finish_quiz_service,
)

router = APIRouter(tags=["quiz"])


@router.post("/quiz/start", response_model=QuizStartOut)
async def start_quiz(db: AsyncSession = Depends(get_session)):
    """Start a new quiz session and return the first question."""
    session_id = await create_quiz_session(db)
    first_question = await get_first_question(db)

    if not first_question:
        raise HTTPException(status_code=404, detail="No questions available")

    await ensure_user_progress(db, session_id, "")

    options_out = [
        AnswerOptionOut(option_id=opt.id, text=opt.text)
        for opt in first_question.options
    ]

    # Count total questions
    count_result = await db.execute(select(Question))
    total_qs = len(count_result.scalars().all())

    return QuizStartOut(
        session_id=session_id,
        first_question=QuestionOut(
            question_id=first_question.id,
            question_text=first_question.question_text,
            question_type=first_question.question_type,
            options=options_out,
        ),
        total_questions=total_qs,
    )


@router.post("/quiz/answer", response_model=QuizAnswerOut)
async def answer_question(
    payload: QuizAnswerIn,
    db: AsyncSession = Depends(get_session),
):
    """Submit an answer and get the next question (or finish)."""
    saved = await save_answer(db, payload.session_id, payload.question_id, payload.answers)
    if not saved:
        raise HTTPException(status_code=404, detail="Session not found")

    finished = await is_quiz_finished(db, payload.session_id)
    if finished:
        return QuizAnswerOut(next_question=None, is_finished=True)

    next_q = await get_next_question(db, payload.session_id)
    if not next_q:
        return QuizAnswerOut(next_question=None, is_finished=True)

    options_out = [
        AnswerOptionOut(option_id=opt.id, text=opt.text)
        for opt in next_q.options
    ]

    return QuizAnswerOut(
        next_question=QuestionOut(
            question_id=next_q.id,
            question_text=next_q.question_text,
            question_type=next_q.question_type,
            options=options_out,
        ),
        is_finished=False,
    )


@router.post("/quiz/finish")
async def finish_quiz(
    payload: dict,
    db: AsyncSession = Depends(get_session),
):
    """Finish the quiz (called by frontend when is_finished=true)."""
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    result = await is_quiz_finished(db, session_id)
    # Count answered questions from DB
    from app.services.quiz_service import get_session_answers as get_answers
    answers = await get_answers(db, session_id)

    return {
        "session_id": session_id,
        "finished": result,
        "total_questions_answered": len(answers),
    }
