from fastapi import Depends
from fastapi import Request
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.providers.embedding_provider import EmbeddingProvider
from app.providers.llm import LLMProvider
from app.providers.redis_memory import RedisMemory
from app.providers.vector_store import VectorStore
from app.services.booking import BookingService
from app.services.chat import ChatService
from app.services.chunker import TextChunker
from app.services.parser import DocumentParser
from app.services.prompt_builder import PromptBuilder
from app.services.retriever import Retriever
from app.services.upload import UploadService

from app.repositories.booking_repository import BookingRepository
from app.services.booking import BookingService


def get_db():
    """
    Provide a database session.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_embedding_provider(
    request: Request,
) -> EmbeddingProvider:
    """
    Return the shared embedding provider.
    """

    return request.app.state.embedding


def get_vector_store(
    request: Request,
) -> VectorStore:
    """
    Return the shared Qdrant vector store.
    """

    return request.app.state.vector_store


def get_llm(
    request: Request,
) -> LLMProvider:
    """
    Return the shared LLM provider.
    """

    return request.app.state.llm


def get_redis_memory(
    request: Request,
) -> RedisMemory:
    """
    Return the shared Redis provider.
    """

    return request.app.state.redis


def get_upload_service(
    request: Request,
) -> UploadService:
    """
    Create an UploadService using shared providers.
    """

    return UploadService(
        parser=DocumentParser(),
        chunker=TextChunker(),
        embedding_provider=request.app.state.embedding,
        vector_store=request.app.state.vector_store,
    )

def get_chat_service(
    request: Request,
    db: Session = Depends(get_db),
) -> ChatService:
    """
    Create a ChatService using shared providers.
    """

    retriever = Retriever(
        embedding_provider=request.app.state.embedding,
        vector_store=request.app.state.vector_store,
    )

    prompt_builder = PromptBuilder()

    booking_repository = BookingRepository(db)

    booking_service = BookingService(
        llm=request.app.state.llm,
        repository=booking_repository,
        model=request.app.state.model,
    )

    return ChatService(
        retriever=retriever,
        prompt_builder=prompt_builder,
        llm=request.app.state.llm,
        redis_memory=request.app.state.redis,
        booking_service=booking_service,
        model=request.app.state.model,
    )