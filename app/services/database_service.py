from sqlalchemy.orm import Session

from app.models import Feature, File, Measurement


def create_file_record(
    db: Session,
    *,
    file_id: str,
    filename: str,
    file_type: str,
    stored_filename: str,
    file_size: int,
    feature_count: int,
    crs: str | None,
    status: str,
) -> File:

    file_record = File(
        id=file_id,
        filename=filename,
        file_type=file_type,
        stored_filename=stored_filename,
        file_size=file_size,
        feature_count=feature_count,
        crs=crs,
        status=status,
    )

    db.add(file_record)

    return file_record


def save_features(
    db: Session,
    file_record: File,
    features: list[dict],
    measurements: list[dict],
) -> None:

    measurement_by_feature = {
        measurement["feature_id"]: measurement
        for measurement in measurements
    }

    for feature_data in features:

        feature = Feature(
            file_id=file_record.id,
            feature_index=feature_data["feature_id"],
            geometry_type=feature_data["geometry_type"],
            geometry=feature_data["geometry"],
            crs=feature_data["crs"],
            properties=feature_data["properties"],
        )

        db.add(feature)

        measurement_data = measurement_by_feature.get(
            feature_data["feature_id"]
        )

        if measurement_data:

            measurement = Measurement(
                feature=feature,
                measurement_type=measurement_data[
                    "measurement_type"
                ],
                value=measurement_data["value"],
                unit=measurement_data["unit"],
                status=measurement_data["status"],
            )

            db.add(measurement)