
import hashlib
import hmac
import secrets
import uuid

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(
    user_id: uuid.UUID,
    session_id: uuid.UUID,
) -> str:
    now = utc_now()

    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "type": "access",
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(
            minutes=settings.ACCESS_TOKEN_MINUTES
        ),
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm="HS256",
    )


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=["HS256"],
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        options={
            "require": [
                "sub", "sid", "type",
                "iss", "aud", "iat",
                "nbf", "exp", "jti",
            ],
        },
    )

    if payload.get("type") != "access":
        raise jwt.InvalidTokenError(
            "Invalid token type"
        )

    return payload


def generate_refresh_token(
    session_id: uuid.UUID,
) -> tuple[str, str]:
    secret = secrets.token_urlsafe(48)

    raw_token = f"{session_id}.{secret}"
    token_hash = hash_refresh_token(secret)

    return raw_token, token_hash


def hash_refresh_token(secret: str) -> str:
    return hashlib.sha256(
        secret.encode("utf-8")
    ).hexdigest()


def verify_refresh_secret(
    secret: str,
    expected_hash: str,
) -> bool:
    actual_hash = hash_refresh_token(secret)

    return hmac.compare_digest(
        actual_hash,
        expected_hash,
    )


def parse_refresh_token(
    token: str,
) -> tuple[uuid.UUID, str]:
    session_part, secret = token.split(".", 1)

    session_id = uuid.UUID(session_part)

    if not secret or len(secret) > 256:
        raise ValueError("Malformed refresh token")

    return session_id, secret
