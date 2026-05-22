"""Roadmap service — handles roadmap retrieval with progress."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession import Profession
from app.models.roadmap import Stage, Step
from app.models.progress import UserProgress, CompletedStep
from app.schemas.roadmap import (
    RoadmapOut,
    RoadmapWithProgressOut,
    StageOut,
    StepOut,
    ResourceOut,
    StageProgressOut,
    NextStepOut,
)


async def get_roadmap(
    db: AsyncSession,
    profession_id: str,
    completed_steps: Optional[set[int]] = None,
) -> Optional[RoadmapOut]:
    """Get roadmap for a profession."""
    result = await db.execute(
        select(Profession)
        .where(Profession.id == profession_id)
        .options(selectinload(Profession.stages).selectinload(Stage.steps))
    )
    profession = result.scalar_one_or_none()
    if not profession:
        return None

    stages_out = []
    for stage in profession.stages:
        steps_out = [
            StepOut(
                step_id=step.id,
                title=step.title,
                step_type=step.step_type,
                resources=[
                    ResourceOut(**r) if isinstance(r, dict) else ResourceOut(title=r.get("title", ""), url=r.get("url", ""))
                    for r in (step.resources or [])
                ],
                is_optional=step.is_optional,
                estimated_hours=step.estimated_hours,
                order=step.order,
                completed=step.id in completed_steps if completed_steps is not None else False,
            )
            for step in stage.steps
        ]
        stages_out.append(
            StageOut(
                stage_id=stage.id,
                title=stage.title,
                description=stage.description,
                order=stage.order,
                steps=steps_out,
            )
        )

    return RoadmapOut(
        profession_id=profession.id,
        title=profession.title,
        total_months=12,
        stages=stages_out,
    )


async def get_roadmap_with_progress(
    db: AsyncSession, session_id: str
) -> Optional[RoadmapWithProgressOut]:
    """Get roadmap for the user's selected profession with progress data."""
    # Get user progress
    result = await db.execute(
        select(UserProgress).where(UserProgress.session_id == session_id)
    )
    up = result.scalar_one_or_none()
    if not up or not up.profession_id:
        return None

    # Get completed steps
    completed_result = await db.execute(
        select(CompletedStep).where(CompletedStep.session_id == session_id)
    )
    completed_steps = {cs.step_id for cs in completed_result.scalars().all()}

    # Get roadmap with completed marks
    roadmap = await get_roadmap(db, up.profession_id, completed_steps=completed_steps)
    if not roadmap:
        return None

    # Calculate progress
    total_steps = 0
    completed_count = 0
    stages_progress = []
    next_step_info = None
    found_incomplete = False

    for stage_out in roadmap.stages:
        stage_total = len(stage_out.steps)
        stage_done = sum(1 for s in stage_out.steps if s.step_id in completed_steps)
        stage_progress = (stage_done / stage_total * 100) if stage_total > 0 else 0

        total_steps += stage_total
        completed_count += stage_done

        stages_progress.append(
            StageProgressOut(
                stage_id=stage_out.stage_id,
                title=stage_out.title,
                progress=round(stage_progress, 1),
                steps_total=stage_total,
                steps_done=stage_done,
            )
        )

        # Find next incomplete step (if not already found)
        if not found_incomplete:
            for s in stage_out.steps:
                if s.step_id not in completed_steps and not s.is_optional:
                    next_step_info = NextStepOut(
                        step_id=s.step_id,
                        title=s.title,
                        stage_id=stage_out.stage_id,
                    )
                    found_incomplete = True
                    break

    overall_progress = (completed_count / total_steps * 100) if total_steps > 0 else 0

    return RoadmapWithProgressOut(
        profession_id=roadmap.profession_id,
        title=roadmap.title,
        stages=roadmap.stages,
        overall_progress=round(overall_progress, 1),
        stages_progress=stages_progress,
        next_step=next_step_info,
    )
