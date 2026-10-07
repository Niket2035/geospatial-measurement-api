from fastapi import APIRouter, HTTPException, UploadFile

from app.services.file_processor import save_uploaded_file


router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)


@router.post("/")
async def upload_file(file: UploadFile):
    """
    Upload a KML or ZIP geospatial file.
    """

    try:
        result = await save_uploaded_file(file)

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc