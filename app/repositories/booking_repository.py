from sqlalchemy.orm import Session

from app.db.models import Booking


class BookingRepository:
    """
    Handles booking database operations.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create(
        self,
        name: str,
        email: str,
        date,
        time,
    ) -> Booking:

        booking = Booking(
            name=name,
            email=email,
            date=date,
            time=time,
        )

        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)

        return booking