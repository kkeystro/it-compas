"""Scoring Engine — calculates profession scores based on user answers."""

from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import AnswerOption, Question
from app.models.profession import Profession


async def calculate_scores(
    session: AsyncSession,
    selected_option_ids: Dict[int, List[int]],  # question_id -> [option_ids]
) -> List[tuple]:
    """
    Calculate weighted scores for each profession based on user answers.

    Returns a list of (profession_id, score, title, market_coefficient) sorted descending.
    """
    # Load all professions
    professions_result = await session.execute(select(Profession))
    professions = professions_result.scalars().all()

    if not professions:
        return []

    # Initialize scores dict
    scores: Dict[str, float] = {p.id: 0.0 for p in professions}

    # Calculate weighted sum
    for question_id, option_ids in selected_option_ids.items():
        for opt_id in option_ids:
            result = await session.execute(
                select(AnswerOption).where(AnswerOption.id == opt_id)
            )
            option = result.scalar_one_or_none()
            if option and option.weights:
                for prof_id, weight in option.weights.items():
                    if prof_id in scores:
                        scores[prof_id] += weight

    # Apply market coefficient and prepare result
    results = []
    for prof in professions:
        final_score = scores[prof.id] * prof.market_coefficient
        results.append((prof.id, final_score, prof.title, prof.market_coefficient))

    # Sort descending by score
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def generate_reason(profession_id: str, profession_title: str) -> str:
    """Generate a human-readable reason for recommending this profession."""
    reasons = {
        "frontend": "Ты указал интерес к визуальной части и интерфейсам. Frontend-разработка — отличный выбор для тех, кто хочет быстро видеть результат своей работы.",
        "backend": "Тебе нравится работа с данными и логикой. Backend-разработка — фундаментальное направление с большими карьерными перспективами.",
        "data_science": "Ты проявил интерес к анализу данных и алгоритмам. Data Science — одно из самых перспективных направлений в IT.",
        "devops": "Тебя привлекает автоматизация и инфраструктура. DevOps-инженеры сейчас очень востребованы на рынке.",
        "ux_ui": "Ты обратил внимание на дизайн и пользовательский опыт. UX/UI-дизайнеры создают продукты, которыми приятно пользоваться.",
        "qa": "Ты внимателен к деталям и любишь находить ошибки. QA-тестирование — важнейший этап разработки любого продукта.",
        "analyst": "Тебе нравится анализировать и систематизировать. Системные аналитики — мост между бизнесом и разработкой.",
        "pm": "Ты проявил лидерские качества и интерес к управлению. Product Manager управляет созданием цифровых продуктов.",
    }
    return reasons.get(profession_id, f"Эта профессия ({profession_title}) отлично подходит по твоим навыкам и интересам.")
