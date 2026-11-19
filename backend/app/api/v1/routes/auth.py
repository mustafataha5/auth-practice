
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from typing import Annotated

from fastapi import Cookie, Header, Response
from fastapi.responses import JSONResponse
from app.api.dependencies import get_current_user
from app.core.cookies import (
    COOKIE_NAME,
    set_refresh_cookie,
    clear_refresh_cookie,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    LogoutResponse,
)
from app.services.session_service import (
    InvalidCredentialsError,
    InvalidSessionError,
    login_user,
    refresh_user_session,
    logout_user_session,
)

from app.db.session import get_db
from app.schemas.user import UserRegister, UserResponse
from app.services.auth_service import (
    register_user,
    EmailAlreadyExistsError,
    DefaultRoleNotFoundError,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    try:
        return register_user(db, data)

    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    except DefaultRoleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Registration temporarily unavailable",
        )




def require_cookie_request(
    x_csrf_intent: Annotated[
        str | None,
        Header(alias="X-CSRF-Intent"),
    ] = None,
    origin: Annotated[
        str | None,
        Header(),
    ] = None,
):
    if x_csrf_intent != "1":
        raise HTTPException(
            status_code=403,
            detail="Missing CSRF request header",
        )

    # Only allow these browser origins for local practice.
    if origin is not None and origin not in {
        "http://localhost:4200",
        "http://localhost:8000",
    }:
        raise HTTPException(
            status_code=403,
            detail="Disallowed origin",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        tokens, refresh_token = login_user(
            db, data.email, data.password
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    set_refresh_cookie(response, refresh_token)
    response.headers["Cache-Control"] = "no-store"
    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(require_cookie_request)],
)
def refresh(
    response: Response,
    refresh_token: Annotated[
        str | None, Cookie()
    ] = None,
    db: Session = Depends(get_db),
):
    try:
        if refresh_token is None:
            raise InvalidSessionError()

        tokens, new_refresh = refresh_user_session(
            db, refresh_token
        )

    except InvalidSessionError:
        error_response = JSONResponse(
            status_code=401,
            content={
                "detail": "Invalid refresh session"
            },
        )
        clear_refresh_cookie(error_response)
        error_response.headers["Cache-Control"] = "no-store"
        return error_response

    # Set the newly rotated refresh token
    set_refresh_cookie(response, new_refresh)

    # Prevent token responses from being cached
    response.headers["Cache-Control"] = "no-store"

    return tokens

@router.post(
    "/logout",
    response_model=LogoutResponse,
    dependencies=[Depends(require_cookie_request)],
)
def logout(
    response: Response,
    refresh_token: Annotated[
        str | None, Cookie()
    ] = None,
    db: Session = Depends(get_db),
):
    logout_user_session(db, refresh_token)
    clear_refresh_cookie(response)

    response.headers["Cache-Control"] = "no-store"
    return LogoutResponse()


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
