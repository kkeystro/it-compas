from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterIn(BaseModel):
    email: str
    password: str
    name: str
    session_id: Optional[str] = None



class LoginIn(BaseModel):
    email: str
    password: str


class AuthOut(BaseModel):
    token: str
    user_id: int
    name: str
    email: str


class MeOut(BaseModel):
    user_id: int
    name: str
    email: str


class MyProfileOut(BaseModel):
    user_id: int
    name: str
    email: str
    session_id: Optional[str] = None
    selected_profession: Optional[str] = None

