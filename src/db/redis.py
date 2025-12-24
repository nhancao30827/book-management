from redis import asyncio as redis
from src.config import Config

JTI_EXPIRY = 360

token_blocklist = redis.from_url(
    f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/0",
    decode_responses=True,
)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(jti, "", ex=JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    value = await token_blocklist.get(jti)
    return value is not None
