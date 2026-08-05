from pathlib import Path
import shutil
import tempfile

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.dependencies import get_upload_service
from app.schemas.upload import UploadResponse
from app.services.upload import UploadService

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


@router.post(
    "/",
    response_model=UploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    chunk_strategy: str = Form("fixed"),
    upload_service: UploadService = Depends(
        get_upload_service
    ),
    db: Session = Depends(get_db),
):
    """
    Upload and ingest a document.
    """

    suffix = Path(file.filename).suffix.lower()

    if suffix not in {".pdf", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:

        shutil.copyfileobj(
            file.file,
            temp_file,
        )

        temp_path = Path(temp_file.name)

    try:

        result = upload_service.ingest_document(
            file_path=temp_path,
            chunk_strategy=chunk_strategy,
            db=db,
        )

        return UploadResponse(**result)

    finally:

        if temp_path.exists():
            temp_path.unlink()