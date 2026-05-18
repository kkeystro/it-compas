from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.roadmap import RoadmapOut, RoadmapWithProgressOut
from app.services.roadmap_service import get_roadmap, get_roadmap_with_progress

router = APIRouter(tags=["roadmap"])


@router.get("/roadmap/{profession_id}", response_model=RoadmapOut)
async def get_profession_roadmap(
    profession_id: str,
    db: AsyncSession = Depends(get_session),
):
    """Get the full roadmap for a profession."""
    roadmap = await get_roadmap(db, profession_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="Profession not found")

    return roadmap


@router.get("/roadmap/my/{session_id}", response_model=RoadmapWithProgressOut)
async def get_my_roadmap(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """Get the roadmap with progress for the user's selected profession."""
    roadmap = await get_roadmap_with_progress(db, session_id)
    if not roadmap:
        raise HTTPException(
            status_code=404,
            detail="No roadmap found. Select a profession first.",
        )

    return roadmap
