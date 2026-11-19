
from sqlalchemy.dialects.postgresql import insert

from app.db.session import SessionLocal
from app.models.role import Role


def seed_roles() -> None:
    with SessionLocal.begin() as db:
        statement = (
            insert(Role)
            .values([
                {"name": "USER"},
                {"name": "ADMIN"},
            ])
            .on_conflict_do_nothing(
                index_elements=["name"],
            )
        )

        db.execute(statement)


if __name__ == "__main__":
    seed_roles()
    print("Default roles initialized.")
