from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models import Feature, File, Measurement
from app.services.database_service import (
    create_file_record,
    save_features,
)
from app.services.file_processor import save_uploaded_file
from app.services.geospatial_processor import (
    process_geospatial_file,
)

from app.schemas import (
    FileResponse,
    MeasurementsResponse,
    UploadResponse,
)

logger = logging.getLogger(__name__) 

router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)


@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile,
    db: Session = Depends(get_db),
):

    try:

        upload_result = await save_uploaded_file(file)

        processing_result = process_geospatial_file(
            upload_result["file_path"]
        )

        file_record = create_file_record(
            db,
            file_id=upload_result["id"],
            filename=upload_result["filename"],
            file_type=upload_result["file_type"],
            stored_filename=upload_result["stored_filename"],
            file_size=upload_result["file_size"],
            feature_count=processing_result["feature_count"],
            crs=processing_result["crs"],
            status="COMPLETED",
        )

        save_features(
            db,
            file_record,
            processing_result["features"],
            processing_result["measurements"],
        )

        db.commit()

        return {
            "id": file_record.id,
            "filename": file_record.filename,
            "feature_count": file_record.feature_count,
            "crs": file_record.crs,
            "status": file_record.status,
        }

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        db.rollback()
        
        logger.error(
            "failed to process file: %s", exc, exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file.",
        ) from exc


@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id: str,
    db: Session = Depends(get_db),
):

    file_record = db.scalar(
        select(File).where(
            File.id == file_id
        )
    )

    if file_record is None:

        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    return {
        "id": file_record.id,
        "filename": file_record.filename,
        "file_type": file_record.file_type,
        "file_size": file_record.file_size,
        "feature_count": file_record.feature_count,
        "crs": file_record.crs,
        "status": file_record.status,
        "created_at": file_record.created_at,
    }


@router.get(
    "/{file_id}/measurements/",
    response_model=MeasurementsResponse,
)
def get_measurements(
    file_id: str,
    db: Session = Depends(get_db),
):

    file_record = db.scalar(
        select(File).where(
            File.id == file_id
        )
    )

    if file_record is None:

        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    measurements = db.scalars(
        select(Measurement)
        .join(Feature)
        .where(
            Feature.file_id == file_id
        )
    ).all()

    return {
        "file_id": file_id,
        "measurements": [
            {
                "feature_id": measurement.feature.feature_index,
                "geometry_type": (
                    measurement.feature.geometry_type
                ),
                "measurement_type": (
                    measurement.measurement_type
                ),
                "value": measurement.value,
                "unit": measurement.unit,
                "status": measurement.status,
            }
            for measurement in measurements
        ],
    }