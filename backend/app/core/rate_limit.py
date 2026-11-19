
import hashlib
import math

from fastapi import HTTPException, Request
from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings


redis_client = Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)

# Atomic increment with expiration.
RATE_LIMIT_SCRIPT = """
local n = redis.call('INCR', KEYS[1])
if n == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {n, ttl}
"""


def check_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
) -> None:
    try:
        count, ttl = redis_client.eval(
            RATE_LIMIT_SCRIPT,
            1,
            key,
            window_seconds,
        )
    except RedisError:
        # Do not silently disable auth rate limiting.
        raise HTTPException(
            status_code=503,
            detail="Authentication temporarily unavailable",
        ) from None

    if int(count) > limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again later.",
            headers={
                "Retry-After": str(max(1, int(ttl))),
            },
        )


def client_ip(request: Request) -> str:
    # Use the immediate peer address.
    # Do not trust client-supplied X-Forwarded-For.
    return (
        request.client.host
        if request.client is not None
        else "unknown"
    )


def login_rate_limit(request: Request) -> None:
    ip = client_ip(request)

    check_rate_limit(
        key=f"auth:login:ip:{ip}",
        limit=10,
        window_seconds=60,
    )


def registration_rate_limit(request: Request) -> None:
    ip = client_ip(request)

    check_rate_limit(
        key=f"auth:register:ip:{ip}",
        limit=5,
        window_seconds=3600,
    )
