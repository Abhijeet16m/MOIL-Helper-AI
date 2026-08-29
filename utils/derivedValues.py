import ee

def ndvi(b4, b8):
    return (b8 - b4) / (b8 + b4)


def ndre(b5, b8):
    return (b8 - b5) / (b8 + b5)


# -------------------------
# SIMPLE SPECTRAL RATIOS
# -------------------------

def ratio(band_a, band_b):
    """Generic spectral ratio."""
    return band_a / band_b if band_b != 0 else None


def b4_b3(b3, b4):
    return ratio(b4, b3)


def b4_b2(b2, b4):
    return ratio(b4, b2)


def b8_b4(b4, b8):
    return ratio(b8, b4)


def b8_b5(b5, b8):
    return ratio(b8, b5)


def b8_b6(b6, b8):
    return ratio(b8, b6)


def b8_b7(b7, b8):
    return ratio(b8, b7)


def b8a_b5(b5, b8a):
    return ratio(b8a, b5)


def b11_b8(b8, b11):
    return ratio(b11, b8)


def b12_b8(b8, b12):
    return ratio(b12, b8)


def b11_b12(b11, b12):
    return ratio(b11, b12)


def b12_b11(b11, b12):
    return ratio(b12, b11)


# -------------------------
# DIFFERENCE INDICES
# -------------------------

def normalized_difference(band_a, band_b):
    """General normalized difference."""
    denominator = band_a + band_b

    if denominator == 0:
        return None

    return (band_a - band_b) / denominator


def ndmi(b8, b11):
    """
    Normalized Difference Moisture Index.
    """
    return normalized_difference(b8, b11)


def ndwi(b3, b8):
    """
    McFeeters-style NDWI.
    """
    return normalized_difference(b3, b8)


def mndwi(b3, b11):
    """
    Modified NDWI.
    """
    return normalized_difference(b3, b11)


# -------------------------
# VEGETATION INDICES
# -------------------------

def gndvi(b3, b8):
    """
    Green Normalized Difference Vegetation Index.
    """
    return normalized_difference(b8, b3)


def savi(b4, b8, L=0.5):
    """
    Soil Adjusted Vegetation Index.
    """
    denominator = b8 + b4 + L

    if denominator == 0:
        return None

    return ((b8 - b4) / denominator) * (1 + L)


def osavi(b4, b8):
    """
    Optimized Soil Adjusted Vegetation Index.
    """
    denominator = b8 + b4 + 0.16

    if denominator == 0:
        return None

    return 1.16 * (b8 - b4) / denominator


def msavi(b4, b8):
    """
    Modified Soil Adjusted Vegetation Index.
    """
    value = (
        2 * b8 + 1
        - ((2 * b8 + 1) ** 2 - 8 * (b8 - b4)) ** 0.5
    )

    return value / 2


# -------------------------
# RED-EDGE INDICES
# -------------------------

def ndre_b6(b6, b8):
    """
    NDRE using Sentinel-2 B6.
    """
    return normalized_difference(b8, b6)


def ndre_b7(b7, b8):
    """
    NDRE using Sentinel-2 B7.
    """
    return normalized_difference(b8, b7)


def ndre_b8a(b8a, b5):
    """
    Red-edge normalized difference using B8A and B5.
    """
    return normalized_difference(b8a, b5)


# -------------------------
# REIP
# -------------------------

def reip(b4, b5, b6, b7):
    """
    Sentinel-2 Red Edge Inflection Point approximation.

    REIP = 700 + 40 *
           (((B4 + B7) / 2 - B5) / (B6 - B5))
    """

    denominator = b6 - b5

    if denominator == 0:
        return None

    return 700 + 40 * (
        (((b4 + b7) / 2) - b5) / denominator
    )


# -------------------------
# SWIR / MOISTURE RATIOS
# -------------------------

def swir_ratio(b11, b12):
    """
    SWIR1 / SWIR2.
    """
    return ratio(b11, b12)


def nir_swir_ratio(b8, b11):
    """
    NIR / SWIR1.
    """
    return ratio(b8, b11)


def nir_swir2_ratio(b8, b12):
    """
    NIR / SWIR2.
    """
    return ratio(b8, b12)


# -------------------------
# SPECTRAL CONTRAST
# -------------------------

def spectral_contrast(band_a, band_b):
    """
    Absolute spectral difference.
    """
    return band_a - band_b


def normalized_spectral_contrast(band_a, band_b):
    """
    Normalized spectral contrast.
    """
    return normalized_difference(band_a, band_b)


# -------------------------
# RED-EDGE POSITION / SLOPE
# -------------------------

def red_edge_slope(b5, b7):
    """
    Simple spectral slope between B5 and B7.

    This is a band-to-band slope proxy.
    """
    return (b7 - b5) / 40


def red_edge_slope_b5_b6(b5, b6):
    """
    Spectral slope between B5 and B6.
    """
    return (b6 - b5) / 35


def red_edge_slope_b6_b7(b6, b7):
    """
    Spectral slope between B6 and B7.
    """
    return (b7 - b6) / 30

def vv_vh_ratio(vv, vh):
    """
    Calculate the VV/VH ratio.

    Note:
    VV and VH from Sentinel-1 GRD are in dB.
    For a physically meaningful power ratio,
    convert from dB before calculating the ratio.
    """

    if vv is None or vh is None:
        return None

    return 10 ** ((vv - vh) / 10)


def vv_vh_difference(vv, vh):
    """
    Difference between VV and VH backscatter in dB.
    """

    if vv is None or vh is None:
        return None

    return vv - vh


import ee


def calculate_slope(elevation: ee.Image) -> ee.Image:
    """
    Calculate terrain slope from an elevation DEM.

    Returns:
        ee.Image containing slope in degrees.
    """
    return ee.Terrain.slope(elevation).rename("slope")


def calculate_aspect(elevation: ee.Image) -> ee.Image:
    """
    Calculate terrain aspect from an elevation DEM.

    Returns:
        ee.Image containing aspect in degrees.
    """
    return ee.Terrain.aspect(elevation).rename("aspect")


def calculate_hillshade(elevation: ee.Image) -> ee.Image:
    """
    Calculate hillshade from an elevation DEM.

    Returns:
        ee.Image containing hillshade.
    """
    terrain = ee.Terrain.products(elevation)
    return terrain.select("hillshade").rename("hillshade")


def calculate_curvature(elevation: ee.Image) -> ee.Image:
    """
    Calculate an approximate terrain curvature using the
    second derivative of the elevation surface.

    Returns:
        ee.Image containing curvature.
    """
    kernel = ee.Kernel.laplacian8(normalize=False)

    curvature = elevation.convolve(kernel)

    return curvature.rename("curvature")


def calculate_tpi(elevation: ee.Image, radius: int = 100) -> ee.Image:
    """
    Calculate Topographic Position Index (TPI).

    TPI = elevation - mean elevation of surrounding neighborhood.

    Args:
        elevation: DEM image.
        radius: Neighborhood radius in meters.

    Returns:
        ee.Image containing TPI.
    """
    kernel = ee.Kernel.circle(
        radius=radius,
        units="meters",
        normalize=True
    )

    neighborhood_mean = elevation.reduceNeighborhood(
        reducer=ee.Reducer.mean(),
        kernel=kernel
    )

    tpi = elevation.subtract(neighborhood_mean)

    return tpi.rename("tpi")


def calculate_tri(elevation: ee.Image, radius: int = 100) -> ee.Image:
    """
    Calculate Terrain Ruggedness Index (TRI).

    Measures local elevation variability.

    Args:
        elevation: DEM image.
        radius: Neighborhood radius in meters.

    Returns:
        ee.Image containing TRI.
    """
    kernel = ee.Kernel.circle(
        radius=radius,
        units="meters",
        normalize=False
    )

    mean_elevation = elevation.reduceNeighborhood(
        reducer=ee.Reducer.mean(),
        kernel=kernel
    )

    tri = elevation.subtract(mean_elevation).abs()

    return tri.rename("tri")


def calculate_roughness(elevation: ee.Image, radius: int = 100) -> ee.Image:
    """
    Calculate local terrain roughness using elevation range.

    Roughness = local maximum elevation - local minimum elevation.

    Args:
        elevation: DEM image.
        radius: Neighborhood radius in meters.

    Returns:
        ee.Image containing terrain roughness.
    """
    kernel = ee.Kernel.circle(
        radius=radius,
        units="meters",
        normalize=False
    )

    local_max = elevation.reduceNeighborhood(
        reducer=ee.Reducer.max(),
        kernel=kernel
    )

    local_min = elevation.reduceNeighborhood(
        reducer=ee.Reducer.min(),
        kernel=kernel
    )

    roughness = local_max.subtract(local_min)

    return roughness.rename("roughness")