from pydantic import BaseModel
from typing import List, Optional


class AnswerOptionOut(BaseModel):
    option_id: int
    text: str

    class Config:
        from_attributes = True


class QuestionOut(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    options: List[AnswerOptionOut]

    class Config:
        from_attributes = True


class AnswerOptionIn(BaseModel):
    option_id: int


class QuizAnswerIn(BaseModel):
    session_id: str
    question_id: int
    answers: List[int]  # list of selected option_ids


class QuizAnswerOut(BaseModel):
    next_question: Optional[QuestionOut] = None
    is_finished: bool


class QuizStartOut(BaseModel):
    session_id: str
    first_question: QuestionOut
