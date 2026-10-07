import geopandas as gpd


def get_measurement_crs(
    gdf: gpd.GeoDataFrame,
) -> str:
    """
    Determine the CRS that should be used for measurements.
    """

    if gdf.empty:
        raise ValueError(
            "Cannot determine measurement CRS for an empty dataset."
        )

    if gdf.crs is None:
        raise ValueError(
            "Input file does not contain a CRS."
        )

    # Already projected - use the existing CRS.
    if not gdf.crs.is_geographic:
        return gdf.crs.to_string()

    # Geographic CRS - estimate an appropriate UTM CRS.
    estimated_crs = gdf.estimate_utm_crs()

    if estimated_crs is None:
        raise ValueError(
            "Unable to determine a suitable projected CRS."
        )

    return estimated_crs.to_string()

def transform_for_measurement(
    gdf: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, str]:
    """
    Transform a GeoDataFrame to a suitable projected CRS
    for area and distance calculations.
    """

    measurement_crs = get_measurement_crs(gdf)

    transformed_gdf = gdf.to_crs(
        measurement_crs
    )

    return transformed_gdf, measurement_crs