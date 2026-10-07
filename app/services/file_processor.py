from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


UPLOAD_DIR = Path("uploads")

ALLOWED_EXTENSIONS = {".kml", ".zip"}

MAX_FILE_SIZE = 50 * 1024 * 1024


async def save_uploaded_file(file: UploadFile) -> dict:
    """
    Validate and save an uploaded geospatial file.
    """

    if not file.filename:
        raise ValueError("Filename is required.")

    original_filename = Path(file.filename).name
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Only .kml and .zip files are allowed."
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid4())

    safe_filename = f"{file_id}{extension}"
    file_path = UPLOAD_DIR / safe_filename

    total_size = 0

    try:
        with file_path.open("wb") as buffer:

            while chunk := await file.read(1024 * 1024):

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise ValueError(
                        "File size exceeds the 50 MB limit."
                    )

                buffer.write(chunk)

    except Exception:
        if file_path.exists():
            file_path.unlink()

        raise

    return {
        "id": file_id,
        "filename": original_filename,
        "file_type": extension.lstrip("."),
        "stored_filename": safe_filename,
        "file_path": str(file_path),
        "file_size": total_size,
        "status": "UPLOADED",
    }
