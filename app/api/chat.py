from fastapi import APIRouter
from fastapi import Depends

from app.api.dependencies import get_chat_service
from app.schemas.chat import ChatRequest
from app.schemas.chat import ChatResponse
from app.services.chat import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    Ask a question about uploaded documents.
    """

    result = chat_service.ask(
        session_id=request.session_id,
        question=request.question,
        top_k=request.top_k,
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        is_booking=result.get("is_booking", False),
        history_size=result.get("history_size", 0),
    )