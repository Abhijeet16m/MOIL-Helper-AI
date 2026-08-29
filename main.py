import ee

ee.Authenticate()
ee.Initialize()

def getBs(lat, lon):
    point = ee.Geometry.Point([lon, lat])
    sentinel2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(point)
        .filterDate("2025-08-28", "2026-08-28")
        .sort("CLOUDY_PIXEL_PERCENTAGE")
    )
    # print("Number of images:", sentinel2.size().getInfo())

    bands = [
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B8A",
        "B11",
        "B12"
    ]
    image = sentinel2.first().select(bands)
    # image = image.select(bands)
    values = image.reduceRegion(
        reducer=ee.Reducer.first(),
        geometry=point,
        scale=10
    )

    # print("\nSentinel-2 values:")
    return values.getInfo()

lat = 21.2514
lon = 81.6296
print(getBs(lat, lon))