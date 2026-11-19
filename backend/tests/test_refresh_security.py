
import pytest

from app.core.tokens import parse_refresh_token
from app.services.session_service import (
    InvalidSessionError,
    login_user,
    refresh_user_session,
)


def create_session(db_session, client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "security@example.com",
            "password": "SecureTestPassword2026!",
        },
    )

    assert response.status_code == 201

    _, token = login_user(
        db_session,
        "security@example.com",
        "SecureTestPassword2026!",
    )

    return token


def test_unknown_secret_does_not_revoke_session(
    client, db_session
):
    original_token = create_session(
        db_session, client
    )

    session_id, _ = parse_refresh_token(
        original_token
    )

    forged_token = (
        f"{session_id}.completely-wrong-secret"
    )

    with pytest.raises(InvalidSessionError):
        refresh_user_session(
            db_session,
            forged_token,
        )

    # Legitimate token must still work.
    tokens, new_token = refresh_user_session(
        db_session,
        original_token,
    )

    assert tokens["access_token"]
    assert new_token != original_token


def test_consumed_token_revokes_session(
    client, db_session
):
    original = create_session(db_session, client)

    _, rotated = refresh_user_session(
        db_session, original
    )

    # An actual consumed token is replayed.
    with pytest.raises(InvalidSessionError):
        refresh_user_session(
            db_session, original
        )

    # Even the newer token must now fail.
    with pytest.raises(InvalidSessionError):
        refresh_user_session(
            db_session, rotated
        )

import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.models.refresh_session import RefreshSession
from app.services.session_service import login_user

from tests.conftest import test_engine


def test_concurrent_refresh():
    email = f"concurrent-{uuid.uuid4()}@example.com"
    password = "SecureConcurrencyPassword2026!"

    # Committed setup visible to independent connections.
    with Session(test_engine) as db:
        user = User(
            email=email,
            password_hash=hash_password(password),
            is_active=True,
        )
        db.add(user)
        db.commit()
        user_id = user.id

        _, original_token = login_user(
            db, email, password
        )

    barrier = Barrier(2)

    def attempt_refresh():
        with Session(test_engine) as db:
            barrier.wait(timeout=10)

            try:
                refresh_user_session(
                    db, original_token
                )
                return "success"
            except InvalidSessionError:
                return "rejected"

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(attempt_refresh)
                for _ in range(2)
            ]

            results = [
                future.result(timeout=15)
                for future in futures
            ]

        assert sorted(results) == [
            "rejected",
            "success",
        ]

        session_id, _ = parse_refresh_token(
            original_token
        )

        with Session(test_engine) as db:
            session = db.get(
                RefreshSession, session_id
            )

            # Strict replay policy: the second attempt
            # consumes an already-rotated token.
            assert session.revoked is True

    finally:
        # Clean up committed test data.
        with Session(test_engine) as db:
            user = db.get(User, user_id)

            if user is not None:
                db.delete(user)
                db.commit()
