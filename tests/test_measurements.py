import geopandas as gpd

from shapely.geometry import LineString, Point, Polygon

from app.services.measurement import calculate_measurements


def test_polygon_area():

    polygon = Polygon([
        (73.8567, 18.5204),
        (73.8667, 18.5204),
        (73.8667, 18.5304),
        (73.8567, 18.5304),
        (73.8567, 18.5204),
    ])

    gdf = gpd.GeoDataFrame(
        geometry=[polygon],
        crs="EPSG:4326",
    )

    results = calculate_measurements(gdf)

    assert len(results) == 1
    assert results[0]["measurement_type"] == "area"
    assert results[0]["unit"] == "m²"
    assert results[0]["value"] > 0


def test_linestring_length():

    line = LineString([
        (73.8567, 18.5204),
        (73.8667, 18.5304),
    ])

    gdf = gpd.GeoDataFrame(
        geometry=[line],
        crs="EPSG:4326",
    )

    results = calculate_measurements(gdf)

    assert len(results) == 1
    assert results[0]["measurement_type"] == "length"
    assert results[0]["unit"] == "m"
    assert results[0]["value"] > 0


def test_point_has_no_measurement():

    point = Point(
        73.8567,
        18.5204,
    )

    gdf = gpd.GeoDataFrame(
        geometry=[point],
        crs="EPSG:4326",
    )

    results = calculate_measurements(gdf)

    assert len(results) == 1
    assert results[0]["measurement_type"] is None
    assert results[0]["value"] is None
    assert results[0]["status"] == "NO_MEASUREMENT"