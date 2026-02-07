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
    ee.Initialize()
    print("Earth Engine initialized successfully.")

# -------------------------
# 2. Input / Output
# -------------------------
INPUT_GPKG = Path("data/processed/lap_locations.gpkg")
# Output name reflects the 1km MODIS LST data
OUTPUT_GPKG = Path("data/processed/lap_locations_LST_1km_complete.gpkg")

gdf = gpd.read_file(INPUT_GPKG, layer="lap_coffee")
print(f"Loaded {gdf.shape[0]} cafe locations. Deduplicating by address...")
gdf.drop_duplicates(subset=['address'], keep='first', inplace=True)
print(f"Processing {gdf.shape[0]} unique cafe locations after deduplication.")


#  DATE RANGES - NOTE: This script will still iterate daily, 
# but the LST value will only change every 8 days (due to the product structure).
DATE_RANGES = [
    ("2024-09-01", "2024-11-30"),
    ("2023-09-01", "2023-11-30"),
    ("2025-09-01", "2025-11-02"),
]
TOTAL_DAYS = sum([(datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days + 1 for start, end in DATE_RANGES])
TOTAL_RECORDS = gdf.shape[0] * TOTAL_DAYS
print(f"Processing a total of {TOTAL_DAYS} days across all years ({TOTAL_RECORDS} total records).")

# ----------------------------------------------------
# 3. Helper: calculate LST for a point and day (1 KM RESOLUTION)
# ----------------------------------------------------
def get_8day_lst(lat, lon, date_str):
    """
    Fetches MODIS 8-day Land Surface Temperature (LST). This is 1km resolution
    and provides a complete time series as an environmental stress proxy.
    """
    # Use MODIS Terra (MOD11A2) LST_Day_1km band
    LST_BAND = 'LST_Day_1km'
    SCALE_FACTOR = 0.02  # Convert LST units (Kelvin * 0.02)
    LST_SCALE = 1000    # 1 km resolution
    
    target_date = ee.Date(date_str)
    point = ee.Geometry.Point([lon, lat])
    
    # Filter the MODIS 8-day LST collection for the single 8-day composite 
    # that covers the target date.
    collection = (ee.ImageCollection("MODIS/061/MOD11A2")
                  .filterDate(target_date.advance(-7, 'day'), target_date.advance(1, 'day'))
                  .filterBounds(point)
                 )

    # Get the single 8-day image (the one whose start date is closest)
    lst_img = collection.select(LST_BAND).first()
  
    if lst_img is None:
        return None
    
    # Process the image: apply scale factor and convert to Celsius for clarity
    def process_lst(img):
        # Apply the scale factor and convert from Kelvin to Celsius (K - 273.15)
        lst_celsius = img.multiply(SCALE_FACTOR).subtract(273.15)
        return lst_celsius.rename('LST_C')

    processed_img = process_lst(lst_img)
    
    try:
        val = processed_img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=LST_SCALE # 1 km resolution
        ).getInfo()
        
        # Return the LST value in Celsius
        return val.get('LST_C')
    except Exception:
        # Catch any GEE errors
        return None

# -------------------------
# 4. Collect daily LST for all cafés
# -------------------------
all_data = []

for start_date, end_date in DATE_RANGES:
    dates = pd.date_range(start_date, end_date)
    print(f"\n--- Starting Data Collection for {start_date} to {end_date} ({len(dates)} days) ---")

    for i, row in gdf.iterrows():
        lat, lon = row.geometry.y, row.geometry.x
        
        print(f" {row['name']} ({lat:.5f}, {lon:.5f}) - Processing {len(dates)} days...")

        for d in dates:
            # Call the synchronous function
            lst_val = get_8day_lst(
                lat, 
                lon, 
                d.strftime('%Y-%m-%d')
            )
            all_data.append({
                "name": row["name"],
                "address": row["address"],
                "lat": lat,
                "lon": lon,
                "date": d.strftime('%Y-%m-%d'),
                "lst_celsius_1km": lst_val # New proxy name
            })

# -------------------------
# 5. Convert to GeoDataFrame and save
# -------------------------
print("\n--- Finalizing Data and Saving to GeoPackage ---")
df = pd.DataFrame(all_data)
# Filter out any lingering None values (should be minimal to none)
df.dropna(subset=['lst_celsius_1km'], inplace=True) 

gdf_out = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.lon, df.lat),
    crs="EPSG:4326"
)

# Save to new output file
gdf_out.to_file(OUTPUT_GPKG, layer="lap_coffee", driver="GPKG")
print(f" Saved COMPLETE 8-day Land Surface Temperature GeoPackage (1 km resolution) to {OUTPUT_GPKG}")
print(f"Total output records: {gdf_out.shape[0]}")