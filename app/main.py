from fastapi import FastAPI

from app.api.routes.files import router as files_router
from app.database import Base, engine
from app.models import File, Feature, Measurement


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Geospatial File Measurement API",
    description=(
        "API for processing geospatial files "
        "and calculating measurements."
    ),
    version="1.0.0",
)


app.include_router(files_router)


@app.get("/")
def root():
    return {
        "message": "Geospatial File Measurement API is running"
    }