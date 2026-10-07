import geopandas as gpd

from app.services.crs import transform_for_measurement


def calculate_measurements(
    gdf: gpd.GeoDataFrame,
) -> list[dict]:
    """
    Calculate measurements for supported geometry types.
    """

    measurement_gdf, measurement_crs = (
        transform_for_measurement(gdf)
    )

    measurements = []

    for index, row in measurement_gdf.iterrows():

        geometry = row.geometry

        if geometry is None:
            measurements.append({
                "feature_id": int(index),
                "geometry_type": None,
                "measurement_type": None,
                "value": None,
                "unit": None,
                "status": "NO_GEOMETRY",
            })

            continue

        geometry_type = geometry.geom_type

        if geometry_type == "Polygon":

            measurements.append({
                "feature_id": int(index),
                "geometry_type": geometry_type,
                "measurement_type": "area",
                "value": float(geometry.area),
                "unit": "m²",
                "status": "COMPLETED",
            })

        elif geometry_type == "LineString":

            measurements.append({
                "feature_id": int(index),
                "geometry_type": geometry_type,
                "measurement_type": "length",
                "value": float(geometry.length),
                "unit": "m",
                "status": "COMPLETED",
            })

        elif geometry_type == "Point":

            measurements.append({
                "feature_id": int(index),
                "geometry_type": geometry_type,
                "measurement_type": None,
                "value": None,
                "unit": None,
                "status": "NO_MEASUREMENT",
            })

        else:

            measurements.append({
                "feature_id": int(index),
                "geometry_type": geometry_type,
                "measurement_type": None,
                "value": None,
                "unit": None,
                "status": "UNSUPPORTED_GEOMETRY",
            })

    return measurements