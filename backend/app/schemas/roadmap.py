from pydantic import BaseModel
from typing import List, Optional


class ResourceOut(BaseModel):
    title: str
    url: str


class StepOut(BaseModel):
    step_id: int
    title: str
    step_type: str
    resources: List[ResourceOut]
    is_optional: bool
    estimated_hours: int
    order: int

    class Config:
        from_attributes = True


class StageOut(BaseModel):
    stage_id: int
    title: str
    description: str
    order: int
    steps: List[StepOut]

    class Config:
        from_attributes = True


class RoadmapOut(BaseModel):
    profession_id: str
    title: str
    total_months: int
    stages: List[StageOut]


class StageProgressOut(BaseModel):
    stage_id: int
    title: str
    progress: float
    steps_total: int
    steps_done: int


class NextStepOut(BaseModel):
    step_id: int
    title: str
    stage_id: int


class RoadmapWithProgressOut(BaseModel):
    profession_id: str
    title: str
    stages: List[StageOut]
    overall_progress: float
    stages_progress: List[StageProgressOut]
    next_step: Optional[NextStepOut] = None
