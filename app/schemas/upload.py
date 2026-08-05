from pydantic import BaseModel


class UploadResponse(BaseModel):
    """
    Response returned after a successful upload.
    """

    document_id: int
    filename: str
    filetype: str
    chunk_strategy: str
    chunks: int
    vectors: int