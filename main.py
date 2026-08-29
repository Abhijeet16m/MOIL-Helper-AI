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


def getNDVI(b4, b8):
    return (b8-b4)/(b8+b4)

def getNDRE(b5, b8):
    return (b8 - b5) / (b8 + b5)


# lat = 21.2514
# lon = 81.6296
# print(getBs(lat, lon))

points = [(23.24909973, 79.35209656)
#,            (23.9640007, 78.29599762), (22.81200027, 76.96800232), (22.61619949, 79.09850311), (23.70219994, 78.62419891), (22.54120064, 79.40969849), (24.16489983, 77.13700104), (22.86359978, 77.05020142), (23.10849953, 78.07430267), (23.36389923, 77.373703)
           ]
for i in points:
    print(getBs(i[0], i[1]))