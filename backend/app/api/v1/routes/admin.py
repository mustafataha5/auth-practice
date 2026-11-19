
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.authorization import require_admin
from app.db.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.schemas.roles import (
    AdminUserResponse,
    AdminStatsResponse,
)


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
    dependencies=[Depends(require_admin)],
)


@router.get(
    "/users",
    response_model=list[AdminUserResponse],
)
def list_users(
    db: Annotated[Session, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
):
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    return db.scalars(
        select(User)
        .order_by(User.created_at, User.id)
        .limit(limit)
        .offset(offset)
    ).all()


@router.get(
    "/stats",
    response_model=AdminStatsResponse,
)
def admin_stats(
    db: Annotated[Session, Depends(get_db)],
):
    total_users = db.scalar(
        select(func.count()).select_from(User)
    )

    active_users = db.scalar(
        select(func.count())
        .select_from(User)
        .where(User.is_active.is_(True))
    )

    admin_users = db.scalar(
        select(func.count(func.distinct(UserRole.user_id)))
        .join(Role, Role.id == UserRole.role_id)
        .where(Role.name == "ADMIN")
    )

    return AdminStatsResponse(
        total_users=total_users or 0,
        active_users=active_users or 0,
        admin_users=admin_users or 0,
    )
