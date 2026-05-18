"""Tests for roadmap endpoints."""

import pytest
from httpx import AsyncClient


class TestRoadmap:
    async def _seed_data(self, db_session):
        """Seed test data: profession with stages and steps."""
        from app.models.profession import Profession
        from app.models.roadmap import Stage, Step

        prof = Profession(id="backend", title="Backend-разработчик", market_coefficient=1.0)
        db_session.add(prof)
        await db_session.flush()

        stage = Stage(profession_id="backend", title="Основы", description="Test", order=0)
        db_session.add(stage)
        await db_session.flush()

        step = Step(stage_id=stage.id, title="Python", step_type="theory", order=0, resources=[])
        db_session.add(step)
        await db_session.commit()

    @pytest.mark.asyncio
    async def test_get_roadmap_not_found(self, client: AsyncClient):
        """Should return 404 for unknown profession."""
        resp = await client.get("/api/v1/roadmap/unknown")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_roadmap(self, client: AsyncClient, db_session):
        """Should return roadmap for existing profession."""
        await self._seed_data(db_session)
        resp = await client.get("/api/v1/roadmap/backend")
        assert resp.status_code == 200
        data = resp.json()
        assert data["profession_id"] == "backend"
        assert len(data["stages"]) > 0
        assert len(data["stages"][0]["steps"]) > 0
