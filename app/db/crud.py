from sqlalchemy.orm import Session

from app.db.models import Booking
from app.db.models import Document


def save_document(
    db: Session,
    document: Document,
) -> Document:
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def save_booking(
    db: Session,
    booking: Booking,
) -> Booking:
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking