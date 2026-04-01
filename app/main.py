from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, documents, rag, roles, users
from app.core.config import settings
from app.db.init_db import seed_roles
from app.db.session import Base, SessionLocal, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(rag.router)
app.include_router(roles.router)
app.include_router(users.router)


@app.get("/")
def health_check():
    return {
        "message": "Financial Document Management API is running.",
        "docs_url": "/docs",
    }
