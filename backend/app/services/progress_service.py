"""Progress service — handles user progress tracking."""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import UserProgress, CompletedStep
from app.models.roadmap import Step, Stage
from app.schemas.progress import ProgressOut, ProgressUpdateOut
from app.schemas.roadmap import StageProgressOut, NextStepOut


async def get_progress(
    db: AsyncSession, session_id: str
) -> Optional[ProgressOut]:
    """Get current progress for the user session."""
    # Get user progress
    result = await db.execute(
        select(UserProgress).where(UserProgress.session_id == session_id)
    )
    up = result.scalar_one_or_none()
    if not up:
        return None

    # Get all steps for the profession
    steps_result = await db.execute(
        select(Step)
        .join(Stage, Step.stage_id == Stage.id)
        .where(Stage.profession_id == up.profession_id)
        .order_by(Stage.order, Step.order)
    )
    all_steps = steps_result.scalars().all()

    # Get completed steps
    completed_result = await db.execute(
        select(CompletedStep).where(CompletedStep.session_id == session_id)
    )
    completed = completed_result.scalars().all()
    completed_step_ids = {cs.step_id for cs in completed}

    # Get stages for grouping
    stages_result = await db.execute(
        select(Stage)
        .where(Stage.profession_id == up.profession_id)
        .order_by(Stage.order)
    )
    stages = stages_result.scalars().all()

    # Calculate per-stage progress
    stage_steps: dict = {}
    for s in stages:
        stage_steps[s.id] = {"title": s.title, "steps": [], "done": 0}

    for step in all_steps:
        if step.stage_id in stage_steps:
            stage_steps[step.stage_id]["steps"].append(step)
            if step.id in completed_step_ids:
                stage_steps[step.stage_id]["done"] += 1

    stages_progress = []
    total_steps = len(all_steps)
    total_done = len(completed_step_ids)
    next_step_info = None
    found_incomplete = False

    for stage in stages:
        sd = stage_steps[stage.id]
        st = len(sd["steps"])
        sdone = sd["done"]
        sp = (sdone / st * 100) if st > 0 else 0

        stages_progress.append(
            StageProgressOut(
                stage_id=stage.id,
                title=sd["title"],
                progress=round(sp, 1),
                steps_total=st,
                steps_done=sdone,
            )
        )

        # Find next incomplete step
        if not found_incomplete:
            for step in sd["steps"]:
                if step.id not in completed_step_ids and not step.is_optional:
                    next_step_info = NextStepOut(
                        step_id=step.id,
                        title=step.title,
                        stage_id=stage.id,
                    )
                    found_incomplete = True
                    break

    overall_progress = (total_done / total_steps * 100) if total_steps > 0 else 0

    return ProgressOut(
        overall_progress=round(overall_progress, 1),
        completed_steps=sorted(completed_step_ids),
        next_step=next_step_info,
        stages_progress=stages_progress,
    )


async def mark_step_completed(
    db: AsyncSession, session_id: str, step_id: int
) -> Optional[ProgressUpdateOut]:
    """Mark a step as completed and return updated progress."""
    # Check step exists
    step_result = await db.execute(select(Step).where(Step.id == step_id))
    step = step_result.scalar_one_or_none()
    if not step:
        return None

    # Check user progress exists
    up_result = await db.execute(
        select(UserProgress).where(UserProgress.session_id == session_id)
    )
    up = up_result.scalar_one_or_none()
    if not up:
        return None

    # Check if already completed
    existing = await db.execute(
        select(CompletedStep).where(
            CompletedStep.session_id == session_id,
            CompletedStep.step_id == step_id,
        )
    )
    if existing.scalar_one_or_none():
        # Already completed — just return current progress
        progress = await get_progress(db, session_id)
        if progress:
            return ProgressUpdateOut(
                success=True,
                new_overall_progress=progress.overall_progress,
            )

    # Mark as completed
    cs = CompletedStep(session_id=session_id, step_id=step_id)
    db.add(cs)
    await db.commit()

    # Calculate new progress
    progress = await get_progress(db, session_id)
    if progress:
        return ProgressUpdateOut(
            success=True,
            new_overall_progress=progress.overall_progress,
        )

    return ProgressUpdateOut(success=True, new_overall_progress=0.0)
