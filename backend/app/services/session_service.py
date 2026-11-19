
import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session


from app.models.refresh_token_history import (
    RefreshTokenHistory,
)

from app.core.tokens import hash_refresh_token
from app.core.config import settings
from app.core.security import verify_password
from app.core.tokens import (
    create_access_token,
    generate_refresh_token,
    parse_refresh_token,
    utc_now,
    verify_refresh_secret,
)
from app.models.user import User
from app.models.refresh_session import RefreshSession


class InvalidCredentialsError(Exception):
    pass


class InvalidSessionError(Exception):
    pass


def build_access_token(
    user_id: uuid.UUID,
    session_id: uuid.UUID,
) -> dict:
    return {
        "access_token": create_access_token(
            user_id, session_id
        ),
        "token_type": "bearer",
        "expires_in": (
            settings.ACCESS_TOKEN_MINUTES * 60
        ),
    }


def login_user(
    db: Session,
    email: str,
    password: str,
) -> tuple[dict, str]:
    user = db.scalar(
        select(User).where(
            User.email == email.lower()
        )
    )

    if (
        user is None
        or not user.is_active
        or not verify_password(
            password,
            user.password_hash,
        )
    ):
        raise InvalidCredentialsError()

    session_id = uuid.uuid4()
    raw_token, token_hash = generate_refresh_token(
        session_id
    )

    session = RefreshSession(
        id=session_id,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=utc_now() + timedelta(
            days=settings.REFRESH_TOKEN_DAYS
        ),
        revoked=False,
    )

    try:
        db.add(session)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return (
        build_access_token(user.id, session.id),
        raw_token,
    )



def refresh_user_session(
    db: Session,
    raw_token: str,
) -> tuple[dict, str]:
    try:
        session_id, secret = parse_refresh_token(
            raw_token
        )
    except (ValueError, AttributeError):
        raise InvalidSessionError() from None

    # PostgreSQL serializes rotations for this session.
    session = db.scalar(
        select(RefreshSession)
        .where(RefreshSession.id == session_id)
        .with_for_update()
    )

    if session is None:
        db.rollback()
        raise InvalidSessionError()

    if session.revoked:
        db.rollback()
        raise InvalidSessionError()

    incoming_hash = hash_refresh_token(secret)

    try:
        # Case 1: Incorrect secret.
        if not verify_refresh_secret(
            secret,
            session.token_hash,
        ):
            known_replay = db.scalar(
                select(RefreshTokenHistory.id)
                .where(
                    RefreshTokenHistory.session_id
                    == session.id,
                    RefreshTokenHistory.token_hash
                    == incoming_hash,
                )
            )

            if known_replay is not None:
                # Previously consumed valid token.
                # Revoke the affected session.
                session.revoked = True
                db.commit()
            else:
                # Unknown secret: do not log out user.
                db.rollback()

            raise InvalidSessionError()

        # Case 2: Expired session.
        if session.expires_at <= utc_now():
            session.revoked = True
            db.commit()
            raise InvalidSessionError()

        user = db.get(User, session.user_id)

        if user is None or not user.is_active:
            session.revoked = True
            db.commit()
            raise InvalidSessionError()

        # Remember the old token before rotation.
        db.add(
            RefreshTokenHistory(
                session_id=session.id,
                token_hash=session.token_hash,
            )
        )

        new_token, new_hash = generate_refresh_token(
            session.id
        )

        session.token_hash = new_hash

        # Commit history and new secret atomically.
        db.commit()

    except InvalidSessionError:
        raise
    except Exception:
        db.rollback()
        raise

    return (
        build_access_token(user.id, session.id),
        new_token,
    )



def logout_user_session(
    db: Session,
    raw_token: str | None,
) -> None:
    if not raw_token:
        return

    try:
        session_id, secret = parse_refresh_token(
            raw_token
        )
    except (ValueError, AttributeError):
        return

    session = db.scalar(
        select(RefreshSession)
        .where(RefreshSession.id == session_id)
        .with_for_update()
    )

    if session is None:
        return

    if not verify_refresh_secret(
        secret, session.token_hash
    ):
        db.rollback()
        return

    session.revoked = True
    db.commit()
