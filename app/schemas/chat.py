from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Incoming chat request.
    """

    session_id: str
    question: str

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class Source(BaseModel):
    """
    Retrieved source chunk.
    """

    document_id: int
    chunk_number: int
    score: float
    text: str


class ChatResponse(BaseModel):
    """
    Chat response returned to the client.
    """

    answer: str
    sources: list[Source]


class ChatMessage(BaseModel):
    """
    Single conversation message.
    """

    role: str
    content: str