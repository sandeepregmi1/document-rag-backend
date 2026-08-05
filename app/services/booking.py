import json
from urllib import response

from app.providers.llm import LLMProvider
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import BookingExtraction


class BookingService:
    """
    Handles interview booking using an LLM.
    """

    EXTRACTION_PROMPT = """
You are an information extraction assistant.

Determine whether the user's message is requesting an interview booking.

Return ONLY valid JSON.

Schema:

{
    "is_booking": true,
    "name": "",
    "email": "",
    "date": "",
    "time": ""
}

Rules:

- Return true only if the user wants to schedule an interview.
- Convert date into YYYY-MM-DD.
- Convert time into HH:MM (24-hour).
- If any field is missing, return null.
- Do not explain anything.
"""

    def __init__(
        self,
        llm: LLMProvider,
        repository: BookingRepository,
        model: str,
    ) -> None:

        self.llm = llm
        self.repository = repository
        self.model = model

    def process(
        self,
        message: str,
    ):

        prompt = (
            self.EXTRACTION_PROMPT
            + "\n\nUser:\n"
            + message
        )

        response = self.llm.generate(
            prompt=prompt,
            model=self.model,
        )

        print("\n===== LLM RESPONSE =====")
        print(response)
        print("========================\n")
        response = response.strip()

        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

            print("\n===== CLEANED RESPONSE =====")
            print(response)
            print("============================\n") 

        booking = BookingExtraction(
         **json.loads(response)
)

        if not booking.is_booking:
            return None

        if (
            not booking.name
            or not booking.email
            or not booking.date
            or not booking.time
        ):
            return {
                "message": (
                    "Missing booking information."
                )
            }

        booking = self.repository.create(
            name=booking.name,
            email=str(booking.email),
            date=booking.date,
            time=booking.time,
        )

        return booking