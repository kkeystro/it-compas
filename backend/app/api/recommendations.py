from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.recommendation import (
    RecommendationListOut,
    SelectProfessionIn,
    SelectProfessionOut,
)
from app.services.recommendation_service import get_recommendations, select_profession

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations/{session_id}", response_model=RecommendationListOut)
async def get_session_recommendations(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """Get top-3 profession recommendations for a completed quiz session."""
    recs = await get_recommendations(db, session_id)
    if not recs:
        raise HTTPException(status_code=404, detail="No recommendations available. Complete the quiz first.")

    return RecommendationListOut(recommendations=recs)


@router.post("/recommendations/select", response_model=SelectProfessionOut)
async def select_recommendation(
    payload: SelectProfessionIn,
    db: AsyncSession = Depends(get_session),
):
    """Select a profession to proceed with the roadmap."""
    success = await select_profession(db, payload.session_id, payload.profession_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profession not found")

    return SelectProfessionOut(
        session_id=payload.session_id,
        selected_profession=payload.profession_id,
    )
