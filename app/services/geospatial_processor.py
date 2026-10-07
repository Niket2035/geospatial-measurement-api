from pathlib import Path

import geopandas as gpd


def read_geospatial_file(file_path: str) -> gpd.GeoDataFrame:
    """
    Read a supported geospatial file and return a GeoDataFrame.
    """

    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".kml":
        return gpd.read_file(
            path,
            driver="KML",
        )

    if extension == ".zip":
        raise ValueError(
            "ZIP files are not supported for direct reading. Please extract the contents and provide a supported geospatial file."
        )

    raise ValueError(
        "Unsupported geospatial file format."
    )
    

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

    return {
        "feature_count": len(features),
        "crs": str(gdf.crs) if gdf.crs else None,
        "features": features,
    }