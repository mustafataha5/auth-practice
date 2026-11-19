
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.authorization import get_user_roles
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.roles import UserRolesResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me/roles",
    response_model=UserRolesResponse,
)
def my_roles(
    current_user: Annotated[
        User, Depends(get_current_user)
    ],
    db: Annotated[Session, Depends(get_db)],
):
    roles = get_user_roles(db, current_user)

    return UserRolesResponse(
        user_id=current_user.id,
        roles=sorted(roles),
    )
