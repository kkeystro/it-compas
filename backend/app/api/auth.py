from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.auth import RegisterIn, LoginIn, AuthOut, MeOut, MyProfileOut
from app.services.auth_service import register_user, login_user, get_current_user, get_user_id_from_token
from app.services.quiz_service import link_session_to_user
from app.services.profile_service import get_my_profile

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=AuthOut)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_session)):
    """Register a new user."""
    result = await register_user(db, body.email, body.password, body.name, session_id=body.session_id)
    if not result:
        raise HTTPException(status_code=409, detail="Email already registered")
    # Link session to user if provided
    if body.session_id and result:
        await link_session_to_user(db, body.session_id, result.user_id)
    return result


@router.post("/auth/login", response_model=AuthOut)
async def login(body: LoginIn, db: AsyncSession = Depends(get_session)):
    """Login user."""
    result = await login_user(db, body.email, body.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return result


@router.get("/auth/me", response_model=MeOut)
async def me(
    authorization: str = Header(""),
    db: AsyncSession = Depends(get_session),
):
    """Get current user info."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization[7:]
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


@router.get("/auth/my-profile", response_model=MyProfileOut)
async def my_profile(
    authorization: str = Header(""),
    db: AsyncSession = Depends(get_session),
):
    """Get current user profile with session and selected profession."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization[7:]
    user_id = await get_user_id_from_token(db, token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    profile = await get_my_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=401, detail="User not found")
    return profile

