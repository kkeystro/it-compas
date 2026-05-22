"""Auth service — JWT-based registration and login."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import AuthOut, MeOut


# Simple token secret — in production, use a proper env secret
_SECRET = hashlib.sha256(b"career-compass-jwt-secret-2026").hexdigest()


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64)
    return f"{salt}:{h.hex()}"


def _check_password(password: str, stored: str) -> bool:
    salt, hx = stored.split(":", 1)
    h = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64)
    return h.hex() == hx


def _make_token(user_id: int) -> str:
    """Simple signed token — HMAC(user_id:expiry)."""
    expiry = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())
    payload = f"{user_id}:{expiry}"
    sig = hmac.new(_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{payload}:{sig}"


def _verify_token(token: str) -> Optional[int]:
    """Verify token and return user_id or None."""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        user_id, expiry, sig = parts
        expected = hmac.new(
            _SECRET.encode(), f"{user_id}:{expiry}".encode(), hashlib.sha256
        ).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected):
            return None
        if int(expiry) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return int(user_id)
    except (ValueError, IndexError):
        return None


async def register_user(
    db: AsyncSession, email: str, password: str, name: str, session_id: Optional[str] = None
) -> Optional[AuthOut]:
    """Register a new user. Returns None if email already exists."""
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        return None

    user = User(
        email=email,
        password_hash=_hash_password(password),
        name=name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = _make_token(user.id)
    return AuthOut(token=token, user_id=user.id, name=user.name, email=user.email)



async def login_user(db: AsyncSession, email: str, password: str) -> Optional[AuthOut]:
    """Login user. Returns None if credentials invalid."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not _check_password(password, user.password_hash):
        return None

    token = _make_token(user.id)
    return AuthOut(token=token, user_id=user.id, name=user.name, email=user.email)


async def get_current_user(db: AsyncSession, token: str) -> Optional[MeOut]:
    """Get current user from token."""
    user_id = _verify_token(token)
    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    return MeOut(user_id=user.id, name=user.name, email=user.email)


async def get_user_id_from_token(db: AsyncSession, token: str) -> Optional[int]:
    """Get user_id from token (for linking sessions)."""
    user_id = _verify_token(token)
    if not user_id:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        return None
    return user_id
