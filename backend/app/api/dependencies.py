
import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.core.tokens import (
    decode_access_token,
    utc_now,
)
from app.db.session import get_db
from app.models.user import User
from app.models.refresh_session import RefreshSession


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        user_id = uuid.UUID(payload["sub"])
        session_id = uuid.UUID(payload["sid"])

    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        KeyError,
    ):
        raise unauthorized from None

    session = db.get(RefreshSession, session_id)

    if (
        session is None
        or session.user_id != user_id
        or session.revoked
        or session.expires_at <= utc_now()
    ):
        raise unauthorized

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise unauthorized

    return user
