from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.health import router as health_router
from app.config.logging import setup_logging
from app.config.settings import settings
from app.db.database import Base
from app.db.database import engine
import app.db.models

from app.providers.embedding_provider import EmbeddingProvider
from app.providers.llm import LLMProvider
from app.providers.redis_memory import RedisMemory
from app.providers.vector_store import VectorStore

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.document import router as document_router



setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    logger.info("Loading embedding model...")

    app.state.embedding = EmbeddingProvider(
        settings.embedding_model
    )

    logger.info("Connecting Redis...")

    app.state.redis = RedisMemory(
        settings.redis_host,
        settings.redis_port,
    )

    logger.info("Connecting Qdrant...")

    app.state.vector_store = VectorStore(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        collection_name=settings.qdrant_collection,
        vector_size=384,
    )

    logger.info("Initializing OpenAI client...")

    app.state.llm = LLMProvider(
        settings.groq_api_key,
    )
    app.state.model = settings.groq_model

    logger.info("Application ready.")

    yield

    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(document_router)



@app.get("/")
async def root():

    return {
        "message": "Document RAG Backend is running"
    }