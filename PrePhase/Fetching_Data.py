import ee
import pandas as pd

# ============================================================
# EARTH ENGINE AUTHENTICATION + INITIALIZATION
# ============================================================
try:
    ee.Initialize(project='your-earth-engine-project') # Replace with your GCP project ID
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# ============================================================
# UNIFIED EXTRACTION FUNCTION (ONE API CALL PER ROW)
# ============================================================

def get_all_environmental_data(lat, lon, start_date, end_date, year):
    """
    Combines Sentinel-2, Sentinel-1, MODIS LST, SRTM Terrain, and CHIRPS 
    into one single unified image, pulling all required metrics in 1 API call.
    """
    point = ee.Geometry.Point([float(lon), float(lat)])
    
    # --------------------------------------------------------
    # A. Sentinel-2 Composite (B2, B4, B11, B12, NDVI, Metal_Stress, Mn_Index)
    # --------------------------------------------------------
    s2_coll = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )
    s2_img = s2_coll.median()
    
    # Add NDVI band: (B8 - B4) / (B8 + B4)
    s2_img = s2_img.addBands(s2_img.normalizedDifference(["B8", "B4"]).rename("NDVI"))
    
    # Add Metal Stress band: (B8 - B5) / (B8 + B5)
    s2_img = s2_img.addBands(s2_img.normalizedDifference(["B8", "B5"]).rename("Metal_Stress"))
    
    # Add Mn_Index band: (B11 - B12) / (B11 + B12) via native normalizedDifference
    s2_img = s2_img.addBands(s2_img.normalizedDifference(["B11", "B12"]).rename("Mn_Index"))
    
    # Isolate relevant Sentinel-2 layers
    s2_final = s2_img.select(["B2", "B4", "B11", "B12", "NDVI", "Metal_Stress", "Mn_Index"])

    # --------------------------------------------------------
    # B. Land Surface Temperature (MODIS)
    # --------------------------------------------------------
    lst_coll = (
        ee.ImageCollection("MODIS/061/MOD11A2")
        .filterBounds(point)
        .filterDate(start_date, end_date)
    )
    lst_img = lst_coll.select("LST_Day_1km").median().multiply(0.02).rename("LST_Kelvin")

    # --------------------------------------------------------
    # C. Radar Backscatter (Sentinel-1 VV)
    # --------------------------------------------------------
    s1_coll = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
    )
    s1_img = s1_coll.select("VV").median().rename("Radar_VV")

    # --------------------------------------------------------
    # D. Terrain Metrics (SRTM Elevation & Derived Slope)
    # --------------------------------------------------------
    srtm = ee.Image("USGS/SRTMGL1_003").select("elevation").rename("Elevation")
    slope = ee.Terrain.slope(srtm).rename("Slope")

    # --------------------------------------------------------
    # E. Precipitation (CHIRPS Annual Sum)
    # --------------------------------------------------------
    chirps_coll = (
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .filterBounds(point)
        .filterDate(f"{year}-01-01", f"{year + 1}-01-01")
    )
    precip_img = chirps_coll.sum().rename("Annual_Precip")

    # --------------------------------------------------------
    # F. Composite Everything and Reduce 
    # --------------------------------------------------------
    # Combine every single layer into a multi-band image stack
    combined_stack = ee.Image.cat([s2_final, lst_img, s1_img, srtm, slope, precip_img])
    
    try:
        # Sample the stack at the point using a custom pixel scale resolution
        values = combined_stack.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=20, # 20m accommodates combined resolutions cleanly
            bestEffort=True
        ).getInfo()
    except Exception as e:
        print(f"Error extracting data at coordinates ({lat}, {lon}): {e}")
        values = None

    # Safe data extraction formatting map to handle missing footprints cleanly
    return {
        "Mn_Index": values.get("Mn_Index") if values else None,
        "NDVI": values.get("NDVI") if values else None,
        "Metal_Stress": values.get("Metal_Stress") if values else None,
        "LST_Kelvin": values.get("LST_Kelvin") if values else None,
        "Radar_VV": values.get("Radar_VV") if values else None,
        "Slope": values.get("Slope") if values else None,
        "Elevation": values.get("Elevation") if values else None,
        "Annual_Precip": values.get("Annual_Precip") if values else None,
        "B2": values.get("B2") if values else None,
        "B4": values.get("B4") if values else None,
        "B11": values.get("B11") if values else None,
        "B12": values.get("B12") if values else None,
    }


# ============================================================
# PROCESSING PIPELINE RUNNER
# ============================================================

if __name__ == '__main__':
    INPUT_FILE = "training_data.csv"
    OUTPUT_FILE = "training_data_complete.csv"

    print(f"Reading input data matrix from: {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    START_DATE = "2025-08-01"
    END_DATE = "2026-08-01"
    YEAR = 2025

    total_rows = len(df)

    for index, row in df.iterrows():
        current_count = index + 1
        print(f"Processing row {current_count}/{total_rows}...")

        lat = row["LATDD"]
        lon = row["LONDD"]

        # Extract all metrics simultaneously in a single network ping
        extracted_metrics = get_all_environmental_data(lat, lon, START_DATE, END_DATE, YEAR)

        # Directly assign dictionary outputs row-by-row into the DataFrame positions
        for column_name, extracted_value in extracted_metrics.items():
            df.loc[index, column_name] = extracted_value

        print(f"Finished extraction for Row {current_count}")

    # Save updated dataset
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Done! Updated complete matrix successfully saved to: {OUTPUT_FILE}")
