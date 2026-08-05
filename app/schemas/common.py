from pydantic import BaseModel


class MessageResponse(BaseModel):
    """
    Generic success message response.
    """

    message: str