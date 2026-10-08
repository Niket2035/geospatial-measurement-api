from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite:///./test_geospatial.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


TEST_FILES_DIR = Path("tests/test_files")

client = TestClient(app)


def test_upload_kml():
    file_path = TEST_FILES_DIR / "test_with_crs.kml"

    with file_path.open("rb") as file:
        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "test_with_crs.kml",
                    file,
                    "application/vnd.google-earth.kml+xml",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["filename"] == "test_with_crs.kml"
    assert data["feature_count"] == 3
    assert data["status"] == "COMPLETED"

    return data["id"]


def test_get_file():
    file_id = test_upload_kml()

    response = client.get(f"/api/files/{file_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == file_id
    assert data["filename"] == "test_with_crs.kml"
    assert data["feature_count"] == 3
    assert data["status"] == "COMPLETED"


def test_get_measurements():
    file_id = test_upload_kml()

    response = client.get(
        f"/api/files/{file_id}/measurements/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["file_id"] == file_id
    assert len(data["measurements"]) == 3

    measurement_types = {
        measurement["measurement_type"]
        for measurement in data["measurements"]
    }

    assert "area" in measurement_types
    assert "length" in measurement_types


def test_file_not_found():
    response = client.get(
        "/api/files/non-existent-file-id"
    )

    assert response.status_code == 404


def test_unsupported_file_type():
    response = client.post(
        "/api/files/",
        files={
            "file": (
                "test.txt",
                b"this is not a geospatial file",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    

def test_upload_shapefile_zip():
    file_path = TEST_FILES_DIR / "test_shapefile.zip"

    with file_path.open("rb") as file:
        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "test_shapefile.zip",
                    file,
                    "application/zip",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["filename"] == "test_shapefile.zip"
    assert data["feature_count"] == 1
    assert data["status"] == "COMPLETED"
    
def test_upload_shapefile_without_crs():
    file_path = TEST_FILES_DIR / "test_shapefile_without_crs.zip"

    with file_path.open("rb") as file:
        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "test_shapefile_without_crs.zip",
                    file,
                    "application/zip",
                )
            },
        )

    assert response.status_code == 400
    assert "CRS" in response.json()["detail"]