import logging

from fastapi import FastAPI

from app.api.health import router as health_router
from app.config.logging import setup_logging
from app.config.settings import settings
from app.db.database import Base
from app.db.database import engine

# import app.db.models  


setup_logging()

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


@app.on_event("startup")
async def startup():
    logger.info("Application started successfully")


app.include_router(health_router)


@app.get("/")
async def root():
    return {
        "message": "Document RAG Backend is running"
    }