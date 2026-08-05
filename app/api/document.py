from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.api.dependencies import get_db
from app.api.dependencies import get_vector_store

from app.db.crud import delete_document
from app.db.crud import get_document
from app.db.crud import get_documents

from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
):
    return get_documents(db)


@router.get("/{document_id}")
def retrieve_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = get_document(
        db,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


@router.delete("/{document_id}")
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    vector_store=Depends(get_vector_store),
):
    document = get_document(
        db,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    vector_store.delete_document(
        document_id=document_id,
    )

    delete_document(
        db,
        document,
    )

    return {
        "message": "Document deleted successfully"
    }