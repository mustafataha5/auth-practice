
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.api.v1.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.admin import router as admin_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)



app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    admin_router,
    prefix="/api/v1",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CSRF_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-CSRF-Intent",
    ],
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
