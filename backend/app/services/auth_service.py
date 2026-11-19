
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.user import UserRegister


class EmailAlreadyExistsError(Exception):
    pass


class DefaultRoleNotFoundError(Exception):
    pass


def register_user(
    db: Session,
    data: UserRegister,
) -> User:
    # 1. Check for an existing email
    existing_user = db.scalar(
        select(User).where(User.email == data.email)
    )

    if existing_user is not None:
        raise EmailAlreadyExistsError()

    # 2. Load the default role
    default_role = db.scalar(
        select(Role).where(Role.name == "USER")
    )

    if default_role is None:
        raise DefaultRoleNotFoundError()

    # 3. Hash the password (never store plaintext)
    hashed_password = hash_password(data.password)

    # 4. Create user in the current transaction
    user = User(
        email=data.email,
        password_hash=hashed_password,
        is_active=True,
    )

    db.add(user)

    try:
        # Obtain the UUID and INSERT the user
        db.flush()

        # 5. Assign USER role
        user_role = UserRole(
            user_id=user.id,
            role_id=default_role.id,
        )

        db.add(user_role)

        # 6. Save user + role atomically
        db.commit()

    except IntegrityError as exc:
        db.rollback()

        # PostgreSQL unique violation (23505)
        if getattr(exc.orig, "sqlstate", None) == "23505":
            # Confirm the conflict was on the email
            constraint = getattr(
                getattr(exc.orig, "diag", None),
                "constraint_name",
                None,
            )

            if constraint in (
                "ix_users_email",
                "uq_users_email",
            ):
                raise EmailAlreadyExistsError() from exc

        raise

    db.refresh(user)

    return user
