import ee
import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import timedelta, datetime # Import datetime for calculations

# -------------------------
# 1. Initialize GEE
# -------------------------
try:
    ee.Initialize()
except Exception:
    ee.Authenticate()
    ee.Initialize()
    print("Earth Engine initialized successfully.")

# -------------------------
# 2. Input / Output (Updated output name)
# -------------------------
INPUT_GPKG = Path("data/processed/lap_locations.gpkg")
# Renaming output to reflect multi-year data
OUTPUT_GPKG = Path("data/processed/lap_locations_nightlights_monthly_multi_year.gpkg")

gdf = gpd.read_file(INPUT_GPKG, layer="lap_coffee")

# Deduplicate for accurate progress reporting
print(f"Loaded {gdf.shape[0]} cafe locations. Deduplicating by address...")
gdf.drop_duplicates(subset=['address'], keep='first', inplace=True)
print(f"Processing {gdf.shape[0]} unique cafe locations after deduplication.")


#  2024 FULL-YEAR DATE RANGES DEFINED HERE
DATE_RANGES = [
    # Autumn 2024 Only (completing full-year dataset)
    ("2024-09-01", "2024-11-30"),  # Autumn 2024 (91 days)
]

# Total days calculation for progress reporting
TOTAL_DAYS = sum([(datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days + 1 for start, end in DATE_RANGES])
TOTAL_RECORDS = gdf.shape[0] * TOTAL_DAYS
print(f"Processing a total of {TOTAL_DAYS} days across all years ({TOTAL_RECORDS} total records).")


# -------------------------
# 3. Helper: get monthly nightlights (No change to function logic)
# -------------------------
def get_monthly_nightlights(lat, lon, date):
    dt = pd.to_datetime(date)
    month_start = dt.replace(day=1)
    month_end = (month_start + pd.offsets.MonthEnd(1))

    # The VIIRS DNB product is ~750m resolution, using scale=500 is fine.
    collection = (ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG")
                  .filterDate(month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d'))
                  .filterBounds(ee.Geometry.Point([lon, lat])))

    mean_img = collection.mean()
    point = ee.Geometry.Point([lon, lat])

    try:
        val = mean_img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=500
        ).getInfo()
        return val.get('avg_rad')
    except Exception:
        return None

# -------------------------
# 4. Collect nightlights for all cafés (Updated loop)
# -------------------------
all_data = []

# Loop through each defined date range
for start_date, end_date in DATE_RANGES:
    dates = pd.date_range(start_date, end_date)
    print(f"\n--- Starting Data Collection for {start_date} to {end_date} ({len(dates)} days) ---")

    for i, row in gdf.iterrows():
        lat, lon = row.geometry.y, row.geometry.x
        print(f" {row['name']} ({lat:.5f}, {lon:.5f}) - Processing {len(dates)} days...")

        for d in dates:
            # The function calculates the monthly average, so the result for all 
            # days in a month will be identical, but the loop covers the full time frame.
            nl_val = get_monthly_nightlights(lat, lon, d)
            all_data.append({
                "name": row["name"],
                "address": row["address"],
                "lat": lat,
                "lon": lon,
                "date": d.strftime('%Y-%m-%d'),
                "nightlight": nl_val
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
print(f" Saved multi-year monthly nightlight GeoPackage to {OUTPUT_GPKG}")
print(f"Total output records: {gdf_out.shape[0]}")