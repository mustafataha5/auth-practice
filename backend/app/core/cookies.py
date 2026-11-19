
from fastapi import Response

from app.core.config import settings

COOKIE_NAME = "refresh_token"
COOKIE_PATH = "/api/v1/auth"


def set_refresh_cookie(
    response: Response,
    token: str,
) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=(
            settings.REFRESH_TOKEN_DAYS
            * 24 * 60 * 60
        ),
        path=COOKIE_PATH,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=COOKIE_NAME,
        path=COOKIE_PATH,
        secure=not settings.DEBUG,
        httponly=True,
        samesite="lax",
    )
