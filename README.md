# Geospatial File Measurement API

A FastAPI service that accepts geospatial files, extracts their features, and
calculates measurements for supported geometry types.

The API supports:

- KML files (`.kml`)
- Shapefiles packaged as ZIP archives (`.zip`)

## Features

- Upload and validate geospatial files.
- Extract feature index, geometry type, geometry, CRS, and properties.
- Calculate polygon area and LineString length.
- Handle points without a measurement.
- Report unsupported geometries without crashing.
- Transform geographic CRS data, such as EPSG:4326, to an appropriate
  projected UTM CRS before calculating area or length.
- Persist uploaded file metadata, features, and measurements in SQLite.
- Enforce a 50 MB upload limit and protect ZIP extraction from path traversal.

## Technology Stack

- Python
- FastAPI
- Uvicorn
- GeoPandas
- Shapely
- SQLAlchemy
- SQLite
- Pytest

## Setup

### Prerequisites

- Python 3.10 or newer
- A virtual environment is recommended

### Install

PowerShell:

```powershell
git clone <your-public-repository-url>
cd geospatial-measurement-api

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell prevents script execution, activate the environment using the
Python executable directly or configure the local execution policy for your
user account.

### Run locally

```powershell
python run.py
```

The server starts at `http://127.0.0.1:8000`.

Interactive API documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

The application creates `geospatial.db` automatically on startup. Uploaded
files are stored in the `uploads/` directory.

### Run tests

```powershell
pytest -q
```

## API

### Upload a file

```http
POST /api/files/
Content-Type: multipart/form-data
```

Example using `curl`:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/files/ `
  -F "file=@tests/test_files/test_with_crs.kml"
```

For a Shapefile, upload a ZIP containing the `.shp`, `.shx`, `.dbf`, and
normally `.prj` files:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/files/ `
  -F "file=@tests/test_files/test_shapefile.zip"
```

Successful response:

```json
{
  "id": "8a1f6f0c-0d40-4f75-aac0-1f5c7d0b9f31",
  "filename": "test_with_crs.kml",
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

Invalid extensions, corrupt archives, missing CRS, empty datasets, and invalid
Shapefile archives return HTTP 400 with a descriptive `detail` message.

### Get file information

```http
GET /api/files/{file_id}
```

Example:

```powershell
curl.exe http://127.0.0.1:8000/api/files/8a1f6f0c-0d40-4f75-aac0-1f5c7d0b9f31
```

Response:

```json
{
  "id": "8a1f6f0c-0d40-4f75-aac0-1f5c7d0b9f31",
  "filename": "test_with_crs.kml",
  "file_type": "kml",
  "file_size": 1542,
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "COMPLETED",
  "created_at": "2026-10-08T06:30:00"
}
```

### Get measurements

```http
GET /api/files/{file_id}/measurements/
```

Example response:

```json
{
  "file_id": "8a1f6f0c-0d40-4f75-aac0-1f5c7d0b9f31",
  "measurements": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "measurement_type": "area",
      "value": 1168186.45,
      "unit": "m²",
      "status": "COMPLETED"
    },
    {
      "feature_id": 1,
      "geometry_type": "Point",
      "measurement_type": null,
      "value": null,
      "unit": null,
      "status": "NO_MEASUREMENT"
    }
  ]
}
```

Measurement statuses include:

- `COMPLETED`: a supported measurement was calculated.
- `NO_MEASUREMENT`: the geometry is a point.
- `NO_GEOMETRY`: the feature has no geometry.
- `UNSUPPORTED_GEOMETRY`: the geometry type is not currently supported.

## Architecture

```text
POST /api/files/
        |
        v
File upload validation and storage
        |
        v
GeoPandas file reader
        |
        +--> Feature extraction
        |
        +--> CRS selection and transformation
        |         |
        |         v
        |    Area/length calculations
        |
        v
SQLAlchemy persistence
        |
        v
Upload response
```

### Application structure

```text
app/
├── api/routes/files.py              HTTP endpoints
├── models/                          SQLAlchemy database models
├── schemas/                         Pydantic response schemas
├── services/file_processor.py       Upload validation and file storage
├── services/geospatial_processor.py KML/Shapefile parsing and feature extraction
├── services/crs.py                  Measurement CRS selection and transformation
├── services/measurement.py          Geometry measurements
├── services/database_service.py     Database persistence helpers
└── database.py                      SQLite engine and session dependency
tests/                               API and service tests
```

### File-processing flow

1. `POST /api/files/` validates the original filename and extension.
2. The upload is saved with a generated UUID filename in `uploads/`.
3. KML files are read directly with GeoPandas.
4. ZIP archives are checked, safely extracted to a temporary directory, and
   the single Shapefile is read.
5. Each feature's index, geometry, CRS, and non-geometry properties are
   extracted.
6. File metadata, feature records, and measurements are committed to SQLite.

### Measurement flow

The service examines each geometry:

- `Polygon`: calculates `geometry.area` in square metres.
- `LineString`: calculates `geometry.length` in metres.
- `Point`: stores a `NO_MEASUREMENT` result.
- Other geometry types: stores an `UNSUPPORTED_GEOMETRY` result.

The API returns a result for every feature, so one unsupported geometry does
not cause the entire upload to fail.

### CRS handling

The original CRS is retained in file and feature metadata. For measurement:

- Missing CRS is rejected because area and length cannot be interpreted
  reliably.
- Existing projected CRS data is used as-is.
- Geographic CRS data, including EPSG:4326, is transformed to a UTM CRS
  estimated from the dataset extent using GeoPandas.
- Measurements are then calculated on the projected geometries rather than
  latitude/longitude degree coordinates.

## Design Decisions

- **FastAPI** was selected for its typed request/response models, automatic
  OpenAPI documentation, and straightforward dependency injection.
- **GeoPandas** provides consistent support for KML and Shapefile data while
  preserving geometry, attributes, and CRS information.
- **SQLite and SQLAlchemy** keep the project easy to run locally while
  preserving a clear path to a production database such as PostgreSQL/PostGIS.
- **Synchronous geospatial processing inside the upload request** keeps the
  implementation simple for the assignment. A production system handling
  large files would move processing to a background worker.
- **One Shapefile per ZIP** avoids ambiguous input selection and makes the
  upload contract explicit.
- **Descriptive measurement statuses** allow unsupported geometries and points
  to be represented without failing the whole request.

## Learning

This project provided practical experience with:

- Designing a FastAPI service around file uploads.
- Reading and normalizing geospatial data with GeoPandas.
- Understanding the difference between geographic and projected CRS.
- Selecting a projected CRS before calculating spatial measurements.
- Safely handling ZIP archives and validating uploaded content.
- Persisting geospatial feature metadata and measurement results with SQLAlchemy.
- Testing API workflows with FastAPI's `TestClient`.

## Future Scope

- Add asynchronous background processing for large uploads.
- Add authentication, authorization, and per-user file ownership.
- Replace local disk storage with object storage such as S3.
- Support GeoJSON and additional Shapefile packaging layouts.
- Add MultiPolygon, MultiLineString, and GeometryCollection measurements.
- Add pagination and filtering for large feature and measurement responses.
- Add database migrations with Alembic.
- Use PostgreSQL/PostGIS for spatial indexing and production-scale queries.
- Add structured logging, monitoring, and automated deployment.
- Add stronger content validation, virus scanning, and configurable limits.

