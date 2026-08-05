from datetime import date as Date
from datetime import time as Time

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr


class BookingExtraction(BaseModel):
    """
    Structured booking information
    extracted by the LLM.
    """

    is_booking: bool

    name: str | None = None

    email: EmailStr | None = None

    date: Date | None = None

    time: Time | None = None


class BookingResponse(BaseModel):
    """
    API response after booking.
    """

    id: int

    name: str

    email: EmailStr

    date: Date

    time: Time

    message: str

    model_config = ConfigDict(
        from_attributes=True,
    )