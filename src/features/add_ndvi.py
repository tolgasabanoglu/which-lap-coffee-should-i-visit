import ee
import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import timedelta, datetime

# -------------------------
# 1. Initialize GEE
# -------------------------
try:
    ee.Initialize()
except Exception:
    # Assuming ee.Authenticate() and ee.Initialize() logic is already handled
    # ee.Authenticate()
    ee.Initialize()
    print("Earth Engine initialized successfully.")

# -------------------------
# 2. Input / Output (Updated output name)
# -------------------------
INPUT_GPKG = Path("data/processed/lap_locations.gpkg")
# Renaming output to reflect multi-year data
OUTPUT_GPKG = Path("data/processed/lap_locations_ndvi_daily_multi_year.gpkg")

gdf = gpd.read_file(INPUT_GPKG, layer="lap_coffee")

# Deduplicate by address before processing to prevent redundant API calls and data duplication
print(f"Loaded {gdf.shape[0]} cafe locations. Deduplicating by address...")
gdf.drop_duplicates(subset=['address'], keep='first', inplace=True)
print(f"Processing {gdf.shape[0]} unique cafe locations after deduplication.")


# 🌟 2024 FULL-YEAR DATE RANGES DEFINED HERE
DATE_RANGES = [
    # Autumn 2024 Only (completing full-year dataset)
    ("2024-09-01", "2024-11-30"),  # Autumn 2024 (91 days)
]

# Total days calculation for progress reporting
TOTAL_DAYS = sum([(datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days + 1 for start, end in DATE_RANGES])
TOTAL_RECORDS = gdf.shape[0] * TOTAL_DAYS
print(f"Processing a total of {TOTAL_DAYS} days across all years ({TOTAL_RECORDS} total records).")
# ----------------------------------------------------
# 3. Helper: calculate NDVI for a point and day
#    Uses temporal smoothing (a window) to mitigate cloud cover gaps.
# ----------------------------------------------------
def get_daily_ndvi(lat, lon, date_str, temporal_window_days=7):
    """
    Fetches Sentinel-2 NDVI, using a temporal window (+/- 7 days)
    to average available observations and fill cloud-related gaps.
    """
    target_date = ee.Date(date_str)
    
    # Define the temporal window: [target_date - window, target_date + window + 1 day]
    start_date_window = target_date.advance(-temporal_window_days, 'day')
    end_date_window = target_date.advance(temporal_window_days + 1, 'day')

    # Filter the Sentinel-2 collection over the time and spatial window
    collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                  .filterDate(start_date_window, end_date_window)
                  .filterBounds(ee.Geometry.Point([lon, lat]))
                  # Filter for cloud cover
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

    # Function to calculate NDVI (B8=NIR, B4=Red)
    def calc_ndvi(img):
        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return ndvi.copyProperties(img, ['system:time_start'])

    ndvi_collection = collection.map(calc_ndvi)
    
    # Calculate the mean NDVI over the temporal window to fill gaps
    mean_ndvi_img = ndvi_collection.mean()

    point = ee.Geometry.Point([lon, lat])
    
    # Sentinel-2 resolution is 10m
    try:
        val = mean_ndvi_img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=10 
        ).getInfo()
        
        return val.get('NDVI')
    except Exception:
        # print(f"Error fetching NDVI for {date_str}: {e}")
        return None

# -------------------------
# 4. Collect daily NDVI for all cafés (Updated loop)
# -------------------------
all_data = []

# Loop through each defined date range
for start_date, end_date in DATE_RANGES:
    dates = pd.date_range(start_date, end_date)
    print(f"\n--- Starting Data Collection for {start_date} to {end_date} ({len(dates)} days) ---")

    for i, row in gdf.iterrows():
        lat, lon = row.geometry.y, row.geometry.x
        print(f"📍 {row['name']} ({lat:.5f}, {lon:.5f}) - Processing {len(dates)} days...")

        for d in dates:
            # Call the function with the 7-day window for gap-filling
            ndvi_val = get_daily_ndvi(
                lat, 
                lon, 
                d.strftime('%Y-%m-%d'), 
                temporal_window_days=7
            )
            all_data.append({
                "name": row["name"],
                "address": row["address"],
                "lat": lat,
                "lon": lon,
                "date": d.strftime('%Y-%m-%d'),
                "ndvi": ndvi_val
            })

# -------------------------
# 5. Convert to GeoDataFrame and save
# -------------------------
print("\n--- Finalizing Data and Saving to GeoPackage ---")
df = pd.DataFrame(all_data)
gdf_out = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.lon, df.lat),
    crs="EPSG:4326"
)

# Save to new output file
gdf_out.to_file(OUTPUT_GPKG, layer="lap_coffee", driver="GPKG")
print(f"✅ Saved gap-filled multi-year daily NDVI GeoPackage to {OUTPUT_GPKG}")
print(f"Total output records: {gdf_out.shape[0]}")