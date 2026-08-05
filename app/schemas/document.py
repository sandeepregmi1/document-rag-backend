from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """
    Document metadata.
    """

    id: int
    filename: str
    filetype: str
    chunk_strategy: str
    uploaded_at: datetime