"""Profile service — returns user session/profile data."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.quiz_session import QuizSession
from app.models.progress import UserProgress
from app.schemas.auth import MyProfileOut


async def get_my_profile(
    db: AsyncSession, user_id: int
) -> Optional[MyProfileOut]:
    """Get user profile with linked session and selected profession."""
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    # Get linked quiz session
    result = await db.execute(
        select(QuizSession).where(QuizSession.user_id == user_id)
    )
    session = result.scalar_one_or_none()

    # Get selected profession from UserProgress
    selected_profession = None
    if session:
        result = await db.execute(
            select(UserProgress).where(UserProgress.session_id == session.session_id)
        )
        up = result.scalar_one_or_none()
        if up and up.profession_id:
            selected_profession = up.profession_id

    return MyProfileOut(
        user_id=user.id,
        name=user.name,
        email=user.email,
        session_id=session.session_id if session else None,
        selected_profession=selected_profession,
    )
