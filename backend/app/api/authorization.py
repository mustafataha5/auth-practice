
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.roles import RoleName
from app.db.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole


def get_user_roles(
    db: Session,
    user: User,
) -> set[str]:
    statement = (
        select(Role.name)
        .join(
            UserRole,
            UserRole.role_id == Role.id,
        )
        .where(UserRole.user_id == user.id)
    )

    return set(db.scalars(statement).all())


def require_roles(
    *allowed_roles: RoleName,
) -> Callable:
    if not allowed_roles:
        raise ValueError(
            "At least one allowed role is required"
        )

    def role_checker(
        current_user: Annotated[
            User, Depends(get_current_user)
        ],
        db: Annotated[Session, Depends(get_db)],
    ) -> User:
        user_roles = get_user_roles(
            db,
            current_user,
        )

        if not user_roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker


require_admin = require_roles(RoleName.ADMIN)
require_user = require_roles(
    RoleName.USER,
    RoleName.ADMIN,
)
