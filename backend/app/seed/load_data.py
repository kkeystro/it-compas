"""Script to load seed data into the database (idempotent)."""

import json
import os
from pathlib import Path

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, init_db
from app.models.profession import Profession
from app.models.question import Question, AnswerOption
from app.models.roadmap import Stage, Step
from app.models.progress import UserProgress, CompletedStep


SEED_DIR = Path(__file__).parent


async def load_professions(session: AsyncSession):
    """Load professions from JSON (idempotent — skip if exists)."""
    with open(SEED_DIR / "professions.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    count_new = 0
    for item in data:
        existing = await session.execute(
            select(Profession).where(Profession.id == item["id"])
        )
        if not existing.scalar_one_or_none():
            prof = Profession(
                id=item["id"],
                title=item["title"],
                description=item.get("description", ""),
                market_coefficient=item.get("market_coefficient", 1.0),
            )
            session.add(prof)
            count_new += 1

    await session.commit()
    print(f"✅ Loaded {count_new} new professions (total {len(data)})")


async def load_questions(session: AsyncSession):
    """Load questions with answer options from JSON (idempotent)."""
    count_result = await session.execute(select(func.count()).select_from(Question))
    existing_count = count_result.scalar()

    if existing_count > 0:
        print(f"⏭️  Questions already loaded ({existing_count}), skipping")
        return

    with open(SEED_DIR / "questions.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        question = Question(
            question_text=item["question_text"],
            question_type=item.get("question_type", "single_choice"),
            order=item.get("order", 0),
        )
        session.add(question)
        await session.flush()

        for opt_data in item.get("options", []):
            option = AnswerOption(
                question_id=question.id,
                text=opt_data["text"],
                weights=opt_data.get("weights", {}),
            )
            session.add(option)

    await session.commit()
    print(f"✅ Loaded {len(data)} questions")


async def load_roadmaps(session: AsyncSession):
    """Load roadmaps from JSON (idempotent — skip if stages exist)."""
    roadmaps_file = SEED_DIR / "roadmaps.json"
    if not roadmaps_file.exists():
        print("⚠️  No roadmaps.json found, skipping roadmap loading")
        return

    count_result = await session.execute(select(func.count()).select_from(Stage))
    if count_result.scalar() > 0:
        print(f"⏭️  Roadmaps already loaded, skipping")
        return

    with open(roadmaps_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_steps = 0
    for roadmap in data:
        prof_id = roadmap.get("profession_id")
        prof_result = await session.execute(
            select(Profession).where(Profession.id == prof_id)
        )
        if not prof_result.scalar_one_or_none():
            print(f"⚠️  Profession '{prof_id}' not found, skipping roadmap")
            continue

        for stage_data in roadmap.get("stages", []):
            stage = Stage(
                profession_id=prof_id,
                title=stage_data["title"],
                description=stage_data.get("description", ""),
                order=stage_data.get("order", 0),
            )
            session.add(stage)
            await session.flush()

            for step_data in stage_data.get("steps", []):
                step = Step(
                    stage_id=stage.id,
                    title=step_data["title"],
                    step_type=step_data.get("step_type", "theory"),
                    resources=step_data.get("resources", []),
                    is_optional=step_data.get("is_optional", False),
                    estimated_hours=step_data.get("estimated_hours", 0),
                    order=step_data.get("order", 0),
                )
                session.add(step)
                total_steps += 1

    await session.commit()
    print(f"✅ Loaded {total_steps} steps across {len(data)} roadmaps")


async def load_all():
    """Clean load: drop all data, then reload from seed files."""
    await init_db()
    async with async_session_factory() as session:
        # Clean slate
        await session.execute(delete(CompletedStep))
        await session.execute(delete(Step))
        await session.execute(delete(Stage))
        await session.execute(delete(AnswerOption))
        await session.execute(delete(Question))
        await session.execute(delete(UserProgress))
        await session.execute(delete(Profession))
        await session.commit()

        await load_professions(session)
        await load_questions(session)
        await load_roadmaps(session)

    print("🎉 Seed data loaded successfully!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(load_all())
