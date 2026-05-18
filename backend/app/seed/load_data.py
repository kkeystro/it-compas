"""Script to load seed data into the database."""

import json
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, init_db
from app.models.profession import Profession
from app.models.question import Question, AnswerOption
from app.models.roadmap import Stage, Step


SEED_DIR = Path(__file__).parent


async def load_professions(session: AsyncSession):
    """Load professions from JSON."""
    with open(SEED_DIR / "professions.json", "r", encoding="utf-8") as f:
        data = json.load(f)

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

    await session.commit()
    print(f"✅ Loaded {len(data)} professions")


async def load_questions(session: AsyncSession):
    """Load questions with answer options from JSON."""
    with open(SEED_DIR / "questions.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        question = Question(
            question_text=item["question_text"],
            question_type=item.get("question_type", "single_choice"),
            order=item.get("order", 0),
        )
        session.add(question)
        await session.flush()  # to get question.id

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
    """Load roadmaps from JSON."""
    roadmaps_file = SEED_DIR / "roadmaps.json"
    if not roadmaps_file.exists():
        print("⚠️  No roadmaps.json found, skipping roadmap loading")
        return

    with open(roadmaps_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for roadmap in data:
        prof_id = roadmap.get("profession_id")
        # Check profession exists
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
                count += 1

    await session.commit()
    print(f"✅ Loaded {count} steps across roadmaps")


async def load_all():
    """Load all seed data."""
    await init_db()
    async with async_session_factory() as session:
        await load_professions(session)
        await load_questions(session)
        await load_roadmaps(session)

    print("🎉 Seed data loaded successfully!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(load_all())
