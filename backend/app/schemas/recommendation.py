from pydantic import BaseModel
from typing import List


class RecommendationOut(BaseModel):
    profession_id: str
    name: str
    score: float
    reason: str
    market_demand: float


class RecommendationListOut(BaseModel):
    recommendations: List[RecommendationOut]


class SelectProfessionIn(BaseModel):
    session_id: str
    profession_id: str


class SelectProfessionOut(BaseModel):
    session_id: str
    selected_profession: str
