from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
import uuid
import logging
from jwt import InvalidTokenError, ExpiredSignatureError
from src.config import Config

password_hash = PasswordHash.recommended()

def generate_password_hash(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def _generate_token(user_id: str, token_type: str, expires_delta: timedelta) -> str:

    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(
        payload,
        Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
    )

def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    delta = expires_delta or timedelta(minutes=15)
    return _generate_token(user_id, "access", delta)

def create_refresh_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    delta = expires_delta or timedelta(days=7)
    return _generate_token(user_id, "refresh", delta)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
        )

    except ExpiredSignatureError:
        logging.warning("JWT expired")

    except InvalidTokenError:
        logging.warning("Invalid JWT")

    except Exception as e:
        logging.exception(e)

    return None