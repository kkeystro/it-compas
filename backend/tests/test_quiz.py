"""Tests for quiz endpoints."""

import pytest
from httpx import AsyncClient


class TestQuizStart:
    @pytest.mark.asyncio
    async def test_start_quiz_no_questions(self, client: AsyncClient):
        """Should return 404 if no questions exist."""
        response = await client.post("/api/v1/quiz/start")
        assert response.status_code == 404



class TestQuizFlow:
    async def _seed_question(self, db_session):
        """Helper to create a test question."""
        from app.models.question import Question, AnswerOption

        q = Question(question_text="Test question?", question_type="single_choice", order=0)
        db_session.add(q)
        await db_session.flush()

        opt = AnswerOption(question_id=q.id, text="Test answer", weights={"backend": 5})
        db_session.add(opt)
        await db_session.commit()
        return q.id

    @pytest.mark.asyncio
    async def test_full_quiz_flow(self, client: AsyncClient, db_session):
        """Test full quiz flow: start -> answer -> finish."""
        # Seed question
        q_id = await self._seed_question(db_session)

        # Start quiz
        resp = await client.post("/api/v1/quiz/start")
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert data["first_question"]["question_id"] == q_id

        session_id = data["session_id"]

        # Answer question
        resp = await client.post(
            "/api/v1/quiz/answer",
            json={
                "session_id": session_id,
                "question_id": q_id,
                "answers": [1],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_finished"] is True
