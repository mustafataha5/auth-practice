
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.api.v1.routes.auth import router as auth_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health(
    db: Session = Depends(get_db),
):
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }
