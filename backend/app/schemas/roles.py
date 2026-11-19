
import uuid

from pydantic import BaseModel, EmailStr


class UserRolesResponse(BaseModel):
    user_id: uuid.UUID
    roles: list[str]


class AdminUserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    admin_users: int
