"""Recommendation service — orchestrates scoring and returns recommendations."""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession import Profession
from app.models.progress import UserProgress
from app.services.scoring import calculate_scores, generate_reason
from app.services.quiz_service import get_session_answers
from app.schemas.recommendation import RecommendationOut


async def get_recommendations(
    db: AsyncSession, session_id: str
) -> List[RecommendationOut]:
    """Calculate and return top-3 recommendations."""
    answers = await get_session_answers(db, session_id)
    if not answers:
        return []

    scores = await calculate_scores(db, answers)

    recommendations = []
    for prof_id, score, title, market_coeff in scores:
        if score <= 0:
            continue
        reason = generate_reason(prof_id, title)
        recommendations.append(
            RecommendationOut(
                profession_id=prof_id,
                name=title,
                score=round(score, 1),
                reason=reason,
                market_demand=market_coeff,
            )
        )
        if len(recommendations) >= 3:
            break

    return recommendations


async def select_profession(
    db: AsyncSession, session_id: str, profession_id: str
) -> bool:
    """Save the user's profession selection."""
    # Check profession exists
    result = await db.execute(
        select(Profession).where(Profession.id == profession_id)
    )
    prof = result.scalar_one_or_none()
    if not prof:
        return False

    # Update or create UserProgress
    result = await db.execute(
        select(UserProgress).where(UserProgress.session_id == session_id)
    )
    up = result.scalar_one_or_none()
    if up:
        up.profession_id = profession_id
    else:
        up = UserProgress(
            session_id=session_id,
            profession_id=profession_id,
            finished_quiz=True,
        )
        db.add(up)

    await db.commit()
    return True
