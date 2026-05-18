"""Tests for recommendation endpoints."""

import pytest
from httpx import AsyncClient


class TestRecommendations:
    async def _seed_data(self, db_session):
        """Seed test data: one profession, one question."""
        from app.models.profession import Profession
        from app.models.question import Question, AnswerOption

        prof = Profession(id="backend", title="Backend-разработчик", market_coefficient=1.0)
        db_session.add(prof)

        q = Question(question_text="Test?", question_type="single_choice", order=0)
        db_session.add(q)
        await db_session.flush()

        opt = AnswerOption(question_id=q.id, text="Test", weights={"backend": 10})
        db_session.add(opt)
        await db_session.commit()
        return q.id

    @pytest.mark.asyncio
    async def test_recommendations_empty(self, client: AsyncClient):
        """Should return 404 for unknown session."""
        resp = await client.get("/api/v1/recommendations/unknown-session")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_recommendations_flow(self, client: AsyncClient, db_session):
        """Test full flow: seed -> start -> answer -> get recommendations."""
        q_id = await self._seed_data(db_session)

        # Start quiz
        resp = await client.post("/api/v1/quiz/start")
        session_id = resp.json()["session_id"]

        # Answer
        await client.post(
            "/api/v1/quiz/answer",
            json={"session_id": session_id, "question_id": q_id, "answers": [1]},
        )

        # Get recommendations
        resp = await client.get(f"/api/v1/recommendations/{session_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["recommendations"]) > 0
        assert data["recommendations"][0]["profession_id"] == "backend"
