
import jwt

from app.core.config import settings
from app.core.tokens import decode_access_token

BASE = "/api/v1/auth"
CSRF_HEADERS = {
    "X-CSRF-Intent": "1",
    "Origin": "http://localhost:4200",
}


def create_account(client):
    response = client.post(
        f"{BASE}/register",
        json={
            "email": "session@example.com",
            "password": "SecureTestPassword2026!",
        },
    )
    assert response.status_code == 201


def do_login(client):
    return client.post(
        f"{BASE}/login",
        json={
            "email": "session@example.com",
            "password": "SecureTestPassword2026!",
        },
    )


def test_login_success(client):
    create_account(client)
    response = do_login(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires_in"] == 900

    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "refresh_token" in response.cookies

    payload = decode_access_token(
        response.json()["access_token"]
    )

    assert payload["type"] == "access"
    assert payload["sub"]
    assert payload["sid"]


def test_login_wrong_password(client):
    create_account(client)

    response = client.post(
        f"{BASE}/login",
        json={
            "email": "session@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post(
        f"{BASE}/login",
        json={
            "email": "missing@example.com",
            "password": "SomePassword2026!",
        },
    )

    assert response.status_code == 401


def test_protected_me(client):
    create_account(client)
    login = do_login(client)

    token = login.json()["access_token"]

    response = client.get(
        f"{BASE}/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["email"]
        == "session@example.com"
    )
    assert "password_hash" not in response.json()


def test_me_without_token(client):
    response = client.get(f"{BASE}/me")
    assert response.status_code == 401


def test_refresh_rotation(client):
    create_account(client)

    login = do_login(client)
    assert login.status_code == 200

    old_cookie = login.cookies.get("refresh_token")

    
    assert old_cookie is not None

    # Request a rotated token
    response = client.post(
        f"{BASE}/refresh",
        headers=CSRF_HEADERS,
    )
    # print("Status:", response.status_code)
    # print("Has Set-Cookie:", "set-cookie" in response.headers)
    # print("Response cookies:", list(response.cookies.keys()))
    # print("Response body keys:", list(response.json().keys()))
    assert response.status_code == 200

    # Read the new cookie directly from the response
    new_cookie = response.cookies.get("refresh_token")

    assert new_cookie is not None
    assert new_cookie != old_cookie

    # Verify the old refresh token cannot be reused
    replay = client.post(
        f"{BASE}/refresh",
        headers={
            **CSRF_HEADERS,
            "Cookie": f"refresh_token={old_cookie}",
        },
    )

    assert replay.status_code == 401



def test_logout_revokes_session(client):
    create_account(client)
    login = do_login(client)

    access_token = login.json()["access_token"]

    response = client.post(
        f"{BASE}/logout",
        headers=CSRF_HEADERS,
    )

    assert response.status_code == 200

    # The old JWT is still cryptographically valid,
    # but its database session is revoked.
    protected = client.get(
        f"{BASE}/me",
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            )
        },
    )

    assert protected.status_code == 401


def test_refresh_requires_csrf_header(client):
    create_account(client)
    do_login(client)

    response = client.post(f"{BASE}/refresh")

    assert response.status_code == 403


def test_invalid_jwt_rejected(client):
    response = client.get(
        f"{BASE}/me",
        headers={
            "Authorization": "Bearer invalid.jwt.token"
        },
    )

    assert response.status_code == 401



def test_refresh_rejects_untrusted_origin(client):
    create_account(client)
    do_login(client)

    response = client.post(
        f"{BASE}/refresh",
        headers={
            "X-CSRF-Intent": "1",
            "Origin": "https://evil.example",
        },
    )

    assert response.status_code == 403


def test_refresh_rejects_missing_origin(client):
    create_account(client)
    do_login(client)

    response = client.post(
        f"{BASE}/refresh",
        headers={"X-CSRF-Intent": "1"},
    )

    assert response.status_code == 403


def test_logout_rejects_cross_site_request(client):
    create_account(client)
    do_login(client)

    response = client.post(
        f"{BASE}/logout",
        headers={
            **CSRF_HEADERS,
            "Sec-Fetch-Site": "cross-site",
        },
    )

    assert response.status_code == 403

