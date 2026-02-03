# src/features/add_historical_weather.py

import geopandas as gpd
import pandas as pd
import requests
from pathlib import Path
from datetime import datetime, timedelta

# -------------------------
# 1. Input & output
# -------------------------
INPUT_GPKG = Path("data/processed/lap_locations.gpkg")
# Updated output name to reflect multi-year data
OUTPUT_GPKG = Path("data/processed/lap_locations_historical_weather_multi_year.gpkg")

# Load LAP Coffee GeoPackage
gdf = gpd.read_file(INPUT_GPKG, layer="lap_coffee")

# Deduplicate for accurate processing (best practice)
print(f"Loaded {gdf.shape[0]} cafe locations. Deduplicating by address...")
gdf.drop_duplicates(subset=['address'], keep='first', inplace=True)
print(f"Processing {gdf.shape[0]} unique cafe locations after deduplication.")


# -------------------------
# 2. Function to determine season
# -------------------------
def get_season(date):
    month = date.month
    if month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Autumn"
    else:  # months 12, 1, 2
        return "Winter"

# -------------------------
# 3. Function to get historical weather from Open-Meteo
# -------------------------
def get_historical_weather(lat, lon, start_date, end_date):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=Europe/Berlin"
    )
    # ⚠️ NOTE: Open-Meteo requests are synchronous and can be slow for many locations/dates.
    res = requests.get(url).json()
    daily = res.get("daily", {})
    if daily:
        records = []
        for i, date_str in enumerate(daily["time"]):
            records.append({
                "weather_date": date_str,
                "temp_max": daily["temperature_2m_max"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "precip_mm": daily["precipitation_sum"][i]
            })
        return records
    return []

# -------------------------
# 4. Define 2024 full year date ranges - ALL SEASONS (Replaced original Section 4)
# -------------------------
DATE_RANGES = [
    # Autumn 2024 Only (completing full-year dataset)
    ("2024-09-01", "2024-11-30"),  # Autumn 2024 (91 days)
]
# Calculate total days for progress reporting
TOTAL_DAYS = sum([(datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days + 1 for start, end in DATE_RANGES])
TOTAL_RECORDS = gdf.shape[0] * TOTAL_DAYS
print(f"Processing a total of {TOTAL_DAYS} days across all years ({TOTAL_RECORDS} total records).")

# -------------------------
# 5. Collect all weather data (Updated loop)
# -------------------------
all_data = []

# Loop through each defined date range
for start_date, end_date in DATE_RANGES:
    print(f"\n--- Starting Weather Data Collection for {start_date} to {end_date} ---")
    
    # Process locations within the current date range
    for i, row in gdf.iterrows():
        lat, lon = row.geometry.y, row.geometry.x
        
        # Call the API once per location per date range
        weather_records = get_historical_weather(lat, lon, start_date, end_date)
        
        print(f"📍 {row['name']} ({lat:.5f}, {lon:.5f}) - Fetched {len(weather_records)} days.")
        
        for record in weather_records:
            record.update({
                "name": row["name"],
                "address": row["address"],
                "lat": lat,
                "lon": lon,
                "rating": row.get("rating", None),
                "user_ratings_total": row.get("user_ratings_total", None),
                # Calculate season for each retrieved date
                "season": get_season(pd.to_datetime(record["weather_date"]))
            })
            all_data.append(record)

# -------------------------
# 6. Convert to GeoDataFrame
# -------------------------
print("\n--- Finalizing Data ---")
df = pd.DataFrame(all_data)
gdf_final = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df.lon, df.lat),
    crs="EPSG:4326"
)

# -------------------------
# 7. Save to GeoPackage
# -------------------------
gdf_final.to_file(OUTPUT_GPKG, layer="lap_coffee", driver="GPKG")
print(f"✅ Saved historical weather GeoPackage to {OUTPUT_GPKG}")
print(f"Total output records: {gdf_final.shape[0]}")