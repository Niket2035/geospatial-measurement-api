from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: str | None
    status: str


class FileResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    feature_count: int
    crs: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeasurementResponse(BaseModel):
    feature_id: int
    geometry_type: str | None
    measurement_type: str | None
    value: float | None
    unit: str | None
    status: str


class MeasurementsResponse(BaseModel):
    file_id: str
    measurements: list[MeasurementResponse]