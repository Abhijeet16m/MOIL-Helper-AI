import ee

ee.Authenticate()
ee.Initialize()

def get_sentinal2(lat, lon, start_date, end_date):
    point = ee.Geometry.Point([lon, lat])
    sentinel2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(point)
        .filterDate(start_date, end_date)
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

def get_sentinel1(lat, lon, start_date, end_date):
    """
    Fetch Sentinel-1 VV and VH backscatter for a given location.

    Parameters
    ----------
    lat : float
        Latitude of the location.
    lon : float
        Longitude of the location.
    start_date : str
        Start date in YYYY-MM-DD format.
    end_date : str
        End date in YYYY-MM-DD format.

    Returns
    -------
    dict
        Dictionary containing VV and VH values.
    """

    point = ee.Geometry.Point([lon, lat])

    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VV"
            )
        )
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VH"
            )
        )
    )

    # Select the most recent available image
    image = collection.sort("system:time_start", False).first()

    values = image.select(["VV", "VH"]).reduceRegion(
        reducer=ee.Reducer.first(),
        geometry=point,
        scale=10
    )

    return values.getInfo()

def get_elevation(lat, lon):
    """
    Get elevation from SRTM DEM for a given location.

    Parameters
    ----------
    lat : float
        Latitude.
    lon : float
        Longitude.

    Returns
    -------
    float
        Elevation in meters above sea level.
    """

    point = ee.Geometry.Point([lon, lat])

    dem = ee.Image("USGS/SRTMGL1_003")

    elevation = dem.reduceRegion(
        reducer=ee.Reducer.first(),
        geometry=point,
        scale=30
    )

    return elevation.get("elevation").getInfo()

def get_lst(
    start_date: str,
    end_date: str,
    lat: float,
    lon: float
) -> ee.Image:

    region = ee.Geometry.Point([lon, lat])

    collection = (
        ee.ImageCollection("MODIS/061/MOD11A2")
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .select("LST_Day_1km")
    )

    return (
        collection
        .mean()
        .multiply(0.02)
        .subtract(273.15)
        .rename("lst")
    )

def get_soil_moisture(
    start_date: str,
    end_date: str,
    lat: float,
    lon: float
) -> ee.Image:
    """
    Fetch SMAP surface soil moisture.

    Dataset:
        NASA/SMAP/SPL3SMP_E/006

    Returns:
        Mean surface soil moisture.
    """
    region = ee.Geometry.Point([lon, lat])

    collection = (
        ee.ImageCollection("NASA/SMAP/SPL3SMP_E/006")
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .select("soil_moisture_am")
    )

    soil_moisture = (
        collection
        .mean()
        .rename("soil_moisture")
    )

    return soil_moisture


def get_radar_texture(lat, lon, start_date, end_date, size=3):
    """
    Calculate Sentinel-1 GLCM radar texture features.

    Parameters
    ----------
    lat : float
        Latitude of the location.
    lon : float
        Longitude of the location.
    start_date : str
        Start date in YYYY-MM-DD format.
    end_date : str
        End date in YYYY-MM-DD format.
    size : int
        GLCM window size in pixels.

    Returns
    -------
    dict
        Dictionary containing radar texture features.
    """

    point = ee.Geometry.Point([lon, lat])

    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VV"
            )
        )
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VH"
            )
        )
        .select(["VV", "VH"])
    )

    # Use the most recent image
    image = collection.sort("system:time_start", False).first()

    # GLCM works with integer values.
    # Sentinel-1 GRD is in dB, so scale before conversion.
    image_scaled = image.multiply(10).toInt16()

    # Calculate GLCM texture
    texture = image_scaled.glcmTexture(size=size)

    # Select useful texture features
    texture = texture.select([
        "VV_contrast",
        "VV_diss",
        "VV_hom",
        "VV_corr",
        "VH_contrast",
        "VH_diss",
        "VH_hom",
        "VH_corr"
    ])

    # Extract values at the requested location
    values = texture.reduceRegion(
        reducer=ee.Reducer.first(),
        geometry=point,
        scale=10
    )

    return values.getInfo()