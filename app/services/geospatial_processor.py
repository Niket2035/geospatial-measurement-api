from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile
from app.services.measurement import calculate_measurements

import geopandas as gpd


def read_geospatial_file(file_path: str) -> gpd.GeoDataFrame:
    """
    Read a supported geospatial file and return a GeoDataFrame.
    """

    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".kml":
        return read_kml(path)

    if extension == ".zip":
        return read_shapefile_zip(path)

    raise ValueError(
        "Unsupported geospatial file format."
    )


def read_kml(path: Path) -> gpd.GeoDataFrame:
    """
    Read a KML file.
    """

    try:
        return gpd.read_file(
            path,
            driver="KML",
        )

    except Exception as exc:
        raise ValueError(
            f"Unable to read KML file: {exc}"
        ) from exc


def safe_extract_zip(zip_file: ZipFile, destination: Path) -> None:
    """
    Safely extract ZIP contents without allowing path traversal.
    """

    destination = destination.resolve()

    for member in zip_file.infolist():

        member_path = (
            destination / member.filename
        ).resolve()

        if not member_path.is_relative_to(destination):
            raise ValueError(
                "ZIP archive contains an unsafe file path."
            )

    zip_file.extractall(destination)


def read_shapefile_zip(path: Path) -> gpd.GeoDataFrame:
    """
    Extract a ZIP archive and read the Shapefile inside it.
    """

    try:
        with ZipFile(path, "r") as zip_file:

            if zip_file.testzip() is not None:
                raise ValueError(
                    "ZIP archive is corrupted."
                )

            members = zip_file.namelist()

            shapefiles = [
                member
                for member in members
                if Path(member).suffix.lower() == ".shp"
            ]

            if not shapefiles:
                raise ValueError(
                    "ZIP file does not contain a Shapefile."
                )

            if len(shapefiles) > 1:
                raise ValueError(
                    "ZIP file contains multiple Shapefiles. "
                    "Please provide a ZIP containing one Shapefile."
                )

            with TemporaryDirectory() as temp_dir:

                safe_extract_zip(
                   zip_file,
                   Path(temp_dir),
                )

                shapefile_path = (
                    Path(temp_dir) / shapefiles[0]
                )

                if not shapefile_path.exists():
                    raise ValueError(
                        "Shapefile could not be extracted."
                    )

                return gpd.read_file(shapefile_path)

    except BadZipFile as exc:

        raise ValueError(
            "Uploaded file is not a valid ZIP archive."
        ) from exc

    except ValueError:
        raise

    except Exception as exc:

        raise ValueError(
            f"Unable to read Shapefile: {exc}"
        ) from exc


def extract_features(gdf: gpd.GeoDataFrame) -> list[dict]:
    """
    Extract feature information from a GeoDataFrame.
    """

    features = []

    crs = str(gdf.crs) if gdf.crs else None

    for index, row in gdf.iterrows():

        geometry = row.geometry

        properties = {}

        for column in gdf.columns:

            if column != "geometry":

                value = row[column]

                if value is not None:
                    properties[column] = str(value)

        feature = {
            "feature_id": int(index),
            "geometry_type": (
                geometry.geom_type
                if geometry is not None
                else None
            ),
            "geometry": (
                geometry.__geo_interface__
                if geometry is not None
                else None
            ),
            "crs": crs,
            "properties": properties,
        }

        features.append(feature)

    return features


def process_geospatial_file(file_path: str) -> dict:
    """
    Read and process a geospatial file.
    """

    gdf = read_geospatial_file(file_path)

    features = extract_features(gdf)

    measurements = calculate_measurements(gdf)

    return {
        "feature_count": len(features),
        "crs": str(gdf.crs) if gdf.crs else None,
        "features": features,
        "measurements": measurements,
    }