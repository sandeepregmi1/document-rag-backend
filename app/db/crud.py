from sqlalchemy.orm import Session

from app.db.models import Booking
from app.db.models import ChunkMetadata
from app.db.models import Document


def save_document(
    db: Session,
    document: Document,
) -> Document:
    """
    Save a document record.
    """
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def save_chunk_metadata(
    db: Session,
    chunk: ChunkMetadata,
) -> ChunkMetadata:
    """
    Save metadata for a document chunk.
    """
    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk


def save_booking(
    db: Session,
    booking: Booking,
) -> Booking:
    """
    Save an interview booking.
    """
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking

def get_documents(
    db: Session,
) -> list[Document]:
    return db.query(Document).all()


def get_document(
    db: Session,
    document_id: int,
) -> Document | None:
    return (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )


def delete_document(
    db: Session,
    document: Document,
) -> None:
    db.delete(document)
    db.commit()


def get_chunk_metadata(
    db: Session,
    document_id: int,
) -> list[ChunkMetadata]:
    return (
        db.query(ChunkMetadata)
        .filter(
            ChunkMetadata.document_id == document_id
        )
        .all()
    )