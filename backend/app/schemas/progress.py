from pydantic import BaseModel
from typing import List, Optional

from app.schemas.roadmap import StageProgressOut, NextStepOut


class ProgressOut(BaseModel):
    overall_progress: float
    completed_steps: List[int]
    next_step: Optional[NextStepOut] = None
    stages_progress: List[StageProgressOut]


class ProgressUpdateOut(BaseModel):
    success: bool
    new_overall_progress: float
