from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.progress import ProgressOut, ProgressUpdateOut
from app.services.progress_service import get_progress, mark_step_completed

router = APIRouter(tags=["progress"])


@router.get("/progress/{session_id}", response_model=ProgressOut)
async def get_session_progress(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """Get current progress for the user session."""
    progress = await get_progress(db, session_id)
    if not progress:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Start the quiz first.",
        )

    return progress


@router.put("/progress/{session_id}/step/{step_id}", response_model=ProgressUpdateOut)
async def complete_step(
    session_id: str,
    step_id: int,
    db: AsyncSession = Depends(get_session),
):
    """Mark a step as completed and return updated progress."""
    result = await mark_step_completed(db, session_id, step_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Session or step not found.",
        )

    return result
