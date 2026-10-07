from fastapi import APIRouter, HTTPException, UploadFile

from app.services.file_processor import save_uploaded_file
from app.services.geospatial_processor import process_geospatial_file


router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)


@router.post("/")
async def upload_file(file: UploadFile):

    try:

        upload_result = await save_uploaded_file(file)

        processing_result = process_geospatial_file(
            upload_result["file_path"]
        )

        return {
            "id": upload_result["id"],
            "filename": upload_result["filename"],
            "feature_count": processing_result["feature_count"],
            "crs": processing_result["crs"],
            "status": "COMPLETED",
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(exc)}",
        ) from exc