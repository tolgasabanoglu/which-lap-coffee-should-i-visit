#!/usr/bin/env python3
"""
Merge LAP Coffee environmental data and prepare for BigQuery upload
Combines weather, NDVI, nightlights, and static features into final dataset
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("LAP Coffee Data Merge & Preparation")
print("=" * 70)
print()

# Paths
DATA_DIR = Path("data/processed")
WEATHER_FILE = DATA_DIR / "lap_locations_historical_weather_multi_year.gpkg"
NDVI_FILE = DATA_DIR / "lap_locations_ndvi_daily_multi_year.gpkg"
NIGHTLIGHTS_FILE = DATA_DIR / "lap_locations_nightlights_monthly_multi_year.gpkg"
STATIC_FILE = DATA_DIR / "lap_locations_with_park_counts.gpkg"
BARS_FILE = DATA_DIR / "lap_locations_with_open_bars.gpkg"
OUTPUT_CSV = DATA_DIR / "lap_locations_final_merged.csv"

# Step 1: Load all data sources
print("Step 1: Loading data files...")
print("-" * 70)

try:
    # Weather data (temp_max, temp_min, precip_mm)
    weather_gdf = gpd.read_file(WEATHER_FILE, layer="lap_coffee")
    print(f"✓ Weather data loaded: {len(weather_gdf)} records")

    # NDVI data
    ndvi_gdf = gpd.read_file(NDVI_FILE, layer="lap_coffee")
    print(f"✓ NDVI data loaded: {len(ndvi_gdf)} records")

    # Nightlights data
    nightlights_gdf = gpd.read_file(NIGHTLIGHTS_FILE, layer="lap_coffee")
    print(f"✓ Nightlights data loaded: {len(nightlights_gdf)} records")

    # Static features (parks count)
    static_gdf = gpd.read_file(STATIC_FILE, layer="lap_coffee")
    print(f"✓ Parks data loaded: {len(static_gdf)} locations")

    # Bars count
    bars_gdf = gpd.read_file(BARS_FILE, layer="lap_coffee")
    print(f"✓ Bars data loaded: {len(bars_gdf)} locations")

except FileNotFoundError as e:
    print(f"\n❌ Error: Missing data file - {e}")
    print("\nMake sure you've run:")
    print("  1. ./collect_full_year_data.sh")
    print("  2. Previous static feature scripts (parks, bars)")
    exit(1)

print()

# Step 2: Merge weather + NDVI + nightlights by date & location
print("Step 2: Merging temporal data (weather + NDVI + nightlights)...")
print("-" * 70)

# Convert to DataFrames for easier merging
weather_df = pd.DataFrame(weather_gdf.drop(columns='geometry'))
ndvi_df = pd.DataFrame(ndvi_gdf.drop(columns='geometry'))
nightlights_df = pd.DataFrame(nightlights_gdf.drop(columns='geometry'))

# Ensure date columns are consistent
if 'weather_date' in weather_df.columns:
    weather_df['date'] = pd.to_datetime(weather_df['weather_date'])
else:
    weather_df['date'] = pd.to_datetime(weather_df['date'])

ndvi_df['date'] = pd.to_datetime(ndvi_df['date'])
nightlights_df['date'] = pd.to_datetime(nightlights_df['date'])

# Merge on address + date (most reliable keys)
merged_temporal = weather_df.merge(
    ndvi_df[['address', 'date', 'ndvi']],
    on=['address', 'date'],
    how='inner'
)

merged_temporal = merged_temporal.merge(
    nightlights_df[['address', 'date', 'nightlight']],
    on=['address', 'date'],
    how='inner'
)

print(f"✓ Temporal data merged: {len(merged_temporal)} daily records")
print()

# Step 3: Add static features (parks, bars)
print("Step 3: Adding static features (parks, bars)...")
print("-" * 70)

# Extract static features
static_df = pd.DataFrame(static_gdf.drop(columns='geometry'))
bars_df = pd.DataFrame(bars_gdf.drop(columns='geometry'))

# Add parks count
merged_with_static = merged_temporal.merge(
    static_df[['address', 'parks_count_1km']],
    on='address',
    how='left'
)

# Add bars count
merged_with_static = merged_with_static.merge(
    bars_df[['address', 'open_bars_count_500m']],
    on='address',
    how='left'
)

print(f"✓ Static features added: parks_count_1km, open_bars_count_500m")
print()

# Step 4: Calculate LST (Land Surface Temperature) as average of temp_max/temp_min
print("Step 4: Calculating derived features...")
print("-" * 70)

merged_with_static['lst_celsius_1km'] = (
    (merged_with_static['temp_max'] + merged_with_static['temp_min']) / 2
)

print(f"✓ Calculated lst_celsius_1km (average of temp_max/temp_min)")
print()

# Step 5: Add season column
print("Step 5: Adding season labels...")
print("-" * 70)

def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:  # 9, 10, 11
        return "Autumn"

merged_with_static['season'] = merged_with_static['date'].apply(get_season)

season_counts = merged_with_static['season'].value_counts()
print("Season distribution:")
for season, count in season_counts.items():
    print(f"  {season}: {count} records")
print()

# Step 6: Create name_updated column (for model training)
print("Step 6: Creating model-compatible name column...")
print("-" * 70)

# Extract street name from address
def extract_street_name(address):
    import re
    street_part = address.split(",")[0].strip() if "," in address else address
    street_name = re.sub(r'\s+\d+[A-Z]?$', '', street_part).strip()
    return street_name if street_name else "Unknown"

merged_with_static['street_name'] = merged_with_static['address'].apply(extract_street_name)
merged_with_static['name_updated'] = "LAP COFFEE_" + merged_with_static['street_name']

unique_locations = merged_with_static['name_updated'].nunique()
print(f"✓ Created name_updated column for {unique_locations} unique locations")
print()

# Step 7: Clean and finalize
print("Step 7: Finalizing dataset...")
print("-" * 70)

# Select final columns (matching training notebook expectations)
final_columns = [
    'date', 'name', 'name_updated', 'address', 'lat', 'lon',
    'rating', 'user_ratings_total', 'season',
    'parks_count_1km', 'open_bars_count_500m',
    'lst_celsius_1km', 'temp_max', 'temp_min', 'precip_mm',
    'ndvi', 'nightlight'
]

# Filter to available columns
available_columns = [col for col in final_columns if col in merged_with_static.columns]
final_df = merged_with_static[available_columns].copy()

# Drop rows with missing critical features
print(f"Dataset size before cleaning: {len(final_df)} rows")

final_df = final_df.dropna(subset=['ndvi', 'parks_count_1km', 'open_bars_count_500m', 'nightlight'])

print(f"Dataset size after removing nulls: {len(final_df)} rows")
print()

# Step 8: Save to CSV
print("Step 8: Saving final dataset...")
print("-" * 70)

final_df.to_csv(OUTPUT_CSV, index=False)

print(f"✓ Saved to: {OUTPUT_CSV}")
print(f"  Total rows: {len(final_df)}")
print(f"  Total columns: {len(final_df.columns)}")
print()

# Print summary statistics
print("=" * 70)
print("Dataset Summary")
print("=" * 70)
print(f"Locations: {final_df['name_updated'].nunique()}")
print(f"Date range: {final_df['date'].min()} to {final_df['date'].max()}")
print(f"Total observations: {len(final_df)}")
print()
print("Feature ranges:")
print(final_df[['parks_count_1km', 'open_bars_count_500m', 'ndvi',
               'nightlight', 'temp_max', 'temp_min', 'precip_mm']].describe())
print()

print("=" * 70)
print("✓ Data preparation complete!")
print("=" * 70)
print()
print("Next steps:")
print("  1. Open Jupyter notebook: jupyter notebook prediction/analysis.ipynb")
print("  2. Update the query to load from CSV instead of BigQuery:")
print(f"     df = pd.read_csv('{OUTPUT_CSV}')")
print("  3. Run cells to train the new RFC model")
print("  4. Model will be saved to: prediction/rfc_model.joblib")
print()
