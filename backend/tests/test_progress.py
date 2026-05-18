"""Tests for progress endpoints."""

import pytest
from httpx import AsyncClient


class TestProgress:
    async def _seed_full_data(self, db_session):
        """Seed profession, stages, steps, and user progress."""
        from app.models.profession import Profession
        from app.models.roadmap import Stage, Step
        from app.models.progress import UserProgress

        prof = Profession(id="backend", title="Backend-разработчик", market_coefficient=1.0)
        db_session.add(prof)
        await db_session.flush()

        stage = Stage(profession_id="backend", title="Основы", order=0)
        db_session.add(stage)
        await db_session.flush()

        step1 = Step(stage_id=stage.id, title="Python", step_type="theory", order=0, resources=[])
        step2 = Step(stage_id=stage.id, title="Git", step_type="practice", order=1, resources=[])
        db_session.add(step1)
        db_session.add(step2)
        await db_session.flush()

        up = UserProgress(session_id="test-session", profession_id="backend", finished_quiz=True)
        db_session.add(up)
        await db_session.commit()
        return step1.id, step2.id

    @pytest.mark.asyncio
    async def test_get_progress_not_found(self, client: AsyncClient):
        """Should return 404 for unknown session."""
        resp = await client.get("/api/v1/progress/unknown")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_progress(self, client: AsyncClient, db_session):
        """Should return progress for existing session."""
        step1_id, step2_id = await self._seed_full_data(db_session)
        resp = await client.get("/api/v1/progress/test-session")
        assert resp.status_code == 200
        data = resp.json()
        assert data["overall_progress"] == 0.0
        assert len(data["stages_progress"]) > 0

    @pytest.mark.asyncio
    async def test_mark_step_completed(self, client: AsyncClient, db_session):
        """Should mark step completed and update progress."""
        step1_id, step2_id = await self._seed_full_data(db_session)

        resp = await client.put(f"/api/v1/progress/test-session/step/{step1_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["new_overall_progress"] == 50.0

        # Mark second step
        resp = await client.put(f"/api/v1/progress/test-session/step/{step2_id}")
        assert resp.status_code == 200
        assert resp.json()["new_overall_progress"] == 100.0
