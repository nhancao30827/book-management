from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import uuid
import jwt

from jwt import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash

from src.config import Config


password_hash = PasswordHash.recommended()


# -------- Password utils --------
def generate_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


# -------- Token helpers --------
def _now() -> datetime:
    return datetime.now(timezone.utc)


def _generate_token(user_id: str, token_type: str, expires_delta: timedelta, extra: dict | None = None) -> str:
    now = _now()
    payload: Dict[str, Any] = {
        "sub": user_id,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
        "iss": "auth-service",
        **(extra or {}), 
    }

    return jwt.encode(
        payload,
        Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
    )


# -------- Token factories --------
def create_access_token(user_id: str, expires: timedelta | None = None, user_role: str = "user") -> str:
    return _generate_token(user_id, "access", expires or timedelta(minutes=15), extra={"role": user_role})


def create_refresh_token(user_id: str, expires: timedelta | None = None) -> str:
    return _generate_token(user_id, "refresh", expires or timedelta(days=7))


# -------- Decode + validation --------
def decode_token(token: str) -> dict:
    """
    Always raises on failure — never returns None.
    """
    try:
        return jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
            options={"require": ["sub", "exp", "jti", "type"]},
        )
    except ExpiredSignatureError:
        raise InvalidTokenError("Token expired")
    except InvalidTokenError as e:
        raise e


# -------- Convenience helpers --------
def is_access_token(payload: dict) -> bool:
    return payload.get("type") == "access"


def is_refresh_token(payload: dict) -> bool:
    return payload.get("type") == "refresh"
