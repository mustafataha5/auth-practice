
from sqlalchemy import select

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole


BASE = "/api/v1"


def register_and_login(client, email="rbac@example.com"):
    password = "SecureTestPassword2026!"

    registration = client.post(
        f"{BASE}/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert registration.status_code == 201

    login = client.post(
        f"{BASE}/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login.status_code == 200

    return login.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def grant_admin(db_session, email="rbac@example.com"):
    user = db_session.scalar(
        select(User).where(User.email == email)
    )
    admin_role = db_session.scalar(
        select(Role).where(Role.name == "ADMIN")
    )

    assert user is not None
    assert admin_role is not None

    db_session.add(
        UserRole(
            user_id=user.id,
            role_id=admin_role.id,
        )
    )
    db_session.commit()


def test_anonymous_admin_access_denied(client):
    response = client.get(f"{BASE}/admin/users")

    assert response.status_code == 401


def test_normal_user_cannot_access_admin(client):
    token = register_and_login(client)

    response = client.get(
        f"{BASE}/admin/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_normal_user_can_get_roles(client):
    token = register_and_login(client)

    response = client.get(
        f"{BASE}/users/me/roles",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["roles"] == ["USER"]


def test_admin_can_list_users(client, db_session):
    token = register_and_login(client)
    grant_admin(db_session)

    response = client.get(
        f"{BASE}/admin/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert any(
        item["email"] == "rbac@example.com"
        for item in response.json()
    )

    for user in response.json():
        assert "password_hash" not in user


def test_admin_can_get_stats(client, db_session):
    token = register_and_login(client)
    grant_admin(db_session)

    response = client.get(
        f"{BASE}/admin/stats",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["total_users"] >= 1
    assert response.json()["admin_users"] >= 1


def test_role_revocation_takes_effect(
    client, db_session
):
    token = register_and_login(client)
    grant_admin(db_session)

    headers = auth_headers(token)

    # Confirm admin access initially works
    assert client.get(
        f"{BASE}/admin/users",
        headers=headers,
    ).status_code == 200

    user = db_session.scalar(
        select(User).where(
            User.email == "rbac@example.com"
        )
    )

    admin_role = db_session.scalar(
        select(Role).where(Role.name == "ADMIN")
    )

    assignment = db_session.get(
        UserRole,
        (user.id, admin_role.id),
    )

    db_session.delete(assignment)
    db_session.commit()

    # Same JWT, but ADMIN role is gone.
    response = client.get(
        f"{BASE}/admin/users",
        headers=headers,
    )

    assert response.status_code == 403


def test_forged_admin_role_in_request_denied(client):
    token = register_and_login(client)

    response = client.get(
        f"{BASE}/admin/users",
        headers={
            **auth_headers(token),
            "X-Role": "ADMIN",
        },
    )

    assert response.status_code == 403
