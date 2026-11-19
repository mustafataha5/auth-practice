
from sqlalchemy import select

from app.core.security import verify_password
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role


def test_registration_success(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "StrongTestPassword2026!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.com"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data

    # Never expose sensitive fields
    assert "password" not in data
    assert "password_hash" not in data

    user = db_session.scalar(
        select(User).where(
            User.email == "test@example.com"
        )
    )

    assert user is not None
    assert user.password_hash != "StrongTestPassword2026!"
    assert user.password_hash.startswith("$argon2id$")
    assert verify_password(
        "StrongTestPassword2026!",
        user.password_hash,
    )


def test_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongTestPassword2026!",
    }

    first = client.post(
        "/api/v1/auth/register", json=payload
    )

    second = client.post(
        "/api/v1/auth/register", json=payload
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_email_normalization(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "TEST@EXAMPLE.COM",
            "password": "StrongTestPassword2026!",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


def test_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "StrongTestPassword2026!",
        },
    )

    assert response.status_code == 422


def test_weak_length_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "short@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_default_user_role(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "roles@example.com",
            "password": "StrongTestPassword2026!",
            "role": "ADMIN",
        },
    )

    assert response.status_code == 201

    user = db_session.scalar(
        select(User).where(
            User.email == "roles@example.com"
        )
    )

    roles = db_session.scalars(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user.id)
    ).all()

    assert [role.name for role in roles] == ["USER"]


def test_same_email_different_case(client):
    first = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Case@Example.com",
            "password": "StrongTestPassword2026!",
        },
    )

    second = client.post(
        "/api/v1/auth/register",
        json={
            "email": "case@example.com",
            "password": "AnotherStrongPassword2026!",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 409
