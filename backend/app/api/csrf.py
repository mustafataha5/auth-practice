
from urllib.parse import urlsplit

from fastapi import Depends, HTTPException, Request

from app.core.config import settings


def reject_csrf() -> None:
    raise HTTPException(
        status_code=403,
        detail="CSRF validation failed",
    )


def origin_from_referer(referer: str) -> str | None:
    try:
        parsed = urlsplit(referer)

        if (
            parsed.scheme not in ("http", "https")
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
        ):
            return None

        return f"{parsed.scheme}://{parsed.netloc}"
    except ValueError:
        return None


def require_csrf(request: Request) -> None:
    headers = request.headers

    # Custom header prevents simple form submissions
    # from satisfying the API's CSRF requirement.
    if headers.get("X-CSRF-Intent") != "1":
        reject_csrf()

    # Cross-site requests are never accepted here.
    if headers.get("Sec-Fetch-Site") == "cross-site":
        reject_csrf()

    origin = headers.get("Origin")

    if origin is None:
        referer = headers.get("Referer")
        if not referer:
            reject_csrf()
        origin = origin_from_referer(referer)

    if origin not in settings.CSRF_ALLOWED_ORIGINS:
        reject_csrf()
