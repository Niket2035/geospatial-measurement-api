import geopandas as gpd
from shapely.geometry import Polygon

from app.services.crs import (
    get_measurement_crs,
    transform_for_measurement,
)


def test_geographic_crs_is_transformed():

    polygon = Polygon([
        (73.8567, 18.5204),
        (73.8667, 18.5204),
        (73.8667, 18.5304),
        (73.8567, 18.5304),
        (73.8567, 18.5204),
    ])

    gdf = gpd.GeoDataFrame(
        {"name": ["Test"]},
        geometry=[polygon],
        crs="EPSG:4326",
    )

    measurement_crs = get_measurement_crs(gdf)

    assert measurement_crs != "EPSG:4326"

    transformed_gdf, transformed_crs = (
        transform_for_measurement(gdf)
    )

    assert transformed_crs != "EPSG:4326"
    assert transformed_gdf.crs is not None