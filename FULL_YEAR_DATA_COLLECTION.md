# LAP Coffee Full-Year Data Collection Guide

Complete guide to collecting all-season data and retraining the RFC model for year-round accuracy.

---

## Overview

**Goal**: Expand training data from 3,440 observations (autumn only) to 7,840+ observations (all seasons)

**Benefits**:
- Better predictions in winter, spring, summer
- More accurate NDVI (greenness) understanding
- Improved weather-café matching across seasons

**Time Required**: 2-3 hours for data collection + 30 minutes for training

---

## Prerequisites

1. **Google Earth Engine Authentication**
   ```bash
   cd /Users/tolgasabanoglu/Desktop/github/which-lap-coffee-should-i-visit
   source venv/bin/activate
   python -c "import ee; ee.Authenticate()"
   ```
   Follow the browser authentication flow.

2. **Verify Environment**
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 1: Collect Environmental Data (2-3 hours)

Run the parallel collection script:

```bash
cd /Users/tolgasabanoglu/Desktop/github/which-lap-coffee-should-i-visit
./collect_full_year_data.sh
```

This will:
- ✓ Fetch weather data for winter/spring/summer 2024 (~10 minutes)
- ✓ Fetch NDVI from Sentinel-2 satellite imagery (~2-3 hours)
- ✓ Fetch nightlight data from VIIRS (~1 hour)
- ✓ Run all three in parallel (limited by slowest: NDVI)
- ✓ Save logs to `logs/` directory

**Monitor progress:**
```bash
# In separate terminals:
tail -f logs/weather_*.log
tail -f logs/ndvi_*.log
tail -f logs/nightlights_*.log
```

**Expected output files:**
- `data/processed/lap_locations_historical_weather_multi_year.gpkg`
- `data/processed/lap_locations_ndvi_daily_multi_year.gpkg`
- `data/processed/lap_locations_nightlights_monthly_multi_year.gpkg`

---

## Step 2: Merge Data Sources (~5 minutes)

Combine all environmental data into a single CSV:

```bash
python merge_and_prepare_data.py
```

This will:
- ✓ Load weather, NDVI, nightlights geopackages
- ✓ Merge on location + date
- ✓ Add static features (parks, bars)
- ✓ Calculate derived features (LST, season)
- ✓ Clean and validate data
- ✓ Save to `data/processed/lap_locations_final_merged.csv`

**Expected result:**
```
Total observations: ~7,840
Seasons: Winter (1,456), Spring (1,472), Summer (1,472), Autumn (3,440)
Locations: 16 LAP Coffee cafés
Features: 8 (parks, bars, temp_max, temp_min, precip, ndvi, nightlight, LST)
```

---

## Step 3: Train RFC Model (~30 minutes)

1. **Open Jupyter Notebook:**
   ```bash
   cd /Users/tolgasabanoglu/Desktop/github/which-lap-coffee-should-i-visit
   jupyter notebook prediction/analysis.ipynb
   ```

2. **Update Cell 1 (Data Loading):**

   Replace the BigQuery query:
   ```python
   # OLD (BigQuery - autumn only)
   query = f"""
       SELECT *
       FROM `{FULL_VIEW_PATH}`
       WHERE season = "Autumn"
       AND nightlight != 0
   """
   df = client.query(query).to_dataframe()
   ```

   With CSV loading:
   ```python
   # NEW (CSV - all seasons)
   import pandas as pd
   df = pd.read_csv('../data/processed/lap_locations_final_merged.csv')

   # Parse date column
   df['date'] = pd.to_datetime(df['date'])

   # Filter nightlight != 0
   df = df[df['nightlight'] != 0]

   print(f"\nDataframe shape: {df.shape}")
   print(f"Season distribution: {df['season'].value_counts().to_dict()}")
   ```

3. **Run All Cells:**
   - Cell 1: Load data ✓
   - Cell 2-4: Data structure ✓
   - Cell 5-7: Feature visualization ✓
   - Cell 8-9: **Train RFC model** ✓
   - Cell 10+: Predictions and validation ✓

4. **Verify Model Output:**
   ```
   Total unique classes (cafés) found: 16
   Total features used: 8

   5-Fold CV Accuracy: 0.9XXX (+/- 0.0XX)
   Best parameters found: {...}
   Test Set Accuracy: 0.9XXX

   Model saved successfully to: prediction/rfc_model.joblib
   LabelEncoder saved successfully to: prediction/label_encoder.joblib
   ```

---

## Step 4: Verify New Model

Test the updated model:

```python
# In Python/notebook
import joblib
import pandas as pd

# Load new model
model = joblib.load('prediction/rfc_model.joblib')
label_encoder = joblib.load('prediction/label_encoder.joblib')

# Test prediction
test_features = {
    'parks_count_1km': 8,
    'open_bars_count_500m': 10,
    'lst_celsius_1km': -2,  # Winter temperature
    'temp_max': 3,
    'temp_min': -5,
    'precip_mm': 0.5,
    'ndvi': 0.25,  # Low winter greenness
    'nightlight': 30
}

X = pd.DataFrame([test_features])
proba = model.predict_proba(X)[0]

# Get top 3 predictions
top_3_idx = proba.argsort()[::-1][:3]
for i, idx in enumerate(top_3_idx, 1):
    cafe = label_encoder.classes_[idx]
    confidence = proba[idx] * 100
    print(f"{i}. {cafe}: {confidence:.1f}%")
```

Expected: Model should now handle winter conditions better (low NDVI, cold temps)

---

## Step 5: Update Dashboard

The dashboard will automatically use the new model since it loads from the same path:
- `prediction/rfc_model.joblib`
- `prediction/label_encoder.joblib`

No code changes needed! Just restart the dashboard:

```bash
cd /Users/tolgasabanoglu/Desktop/github/spatiotemporal
streamlit run dashboard/streamlit_app.py
```

Test recommendations in different seasons to verify improvements.

---

## Expected Improvements

### Before (Autumn-Only Training)
- Training data: 3,440 observations (Sep-Nov)
- NDVI range: 0.15-0.75 (autumn greenness)
- Temperature range: 5-20°C
- **Issue**: Poor predictions in winter (NDVI 0.20-0.40), summer (25-30°C)

### After (Full-Year Training)
- Training data: 7,840 observations (all seasons)
- NDVI range: 0.20-0.80 (full seasonal cycle)
- Temperature range: -5 to 30°C
- **Result**: Accurate predictions year-round

### Feature Importance (Expected Changes)
| Feature | Autumn-Only | Full-Year | Interpretation |
|---------|-------------|-----------|----------------|
| parks_count_1km | 34.8% | ~30% | Less dominant with seasonal variety |
| open_bars_count_500m | 34.4% | ~30% | Stable |
| ndvi | 11.3% | ~15% | More important with seasonal variation |
| nightlight | 10.0% | ~10% | Stable |
| weather | <20% | ~15% | More relevant across seasons |

---

## Troubleshooting

### Earth Engine Authentication Error
```
ee.EEException: Please authorize access to your Earth Engine account
```
**Fix:**
```bash
python -c "import ee; ee.Authenticate()"
```

### Missing Geopackage Files
```
FileNotFoundError: data/processed/lap_locations_with_park_counts.gpkg
```
**Fix:** Ensure you've run the static feature scripts first:
```bash
python src/features/add_nearest_parks.py
python src/features/add_numberofopenbars.py
```

### Memory Error During NDVI Collection
```
MemoryError: Unable to allocate array
```
**Fix:** Reduce the date range or process in smaller chunks

### Model Training Takes Too Long
**Expected**: 5-10 minutes for GridSearchCV with 5-fold CV
**If longer**: Reduce `param_grid` in Cell 8 of notebook

---

## Maintenance

### Annual Update (Recommended)
Collect new data each year to keep the model fresh:
1. Update `DATE_RANGES` in feature scripts to include previous year
2. Re-run collection and training pipeline
3. Compare model accuracy (should remain ~96% if data quality is good)

### Quarterly Validation
Test model predictions quarterly to catch seasonal drift:
```python
# Test in each season
test_predictions_by_season(model, df, season='Winter')
```

---

## Quick Reference

**Full pipeline (one-shot):**
```bash
cd /Users/tolgasabanoglu/Desktop/github/which-lap-coffee-should-i-visit

# Authenticate GEE (first time only)
python -c "import ee; ee.Authenticate()"

# Collect data (2-3 hours)
./collect_full_year_data.sh

# Merge data (5 minutes)
python merge_and_prepare_data.py

# Train model (30 minutes - in Jupyter)
jupyter notebook prediction/analysis.ipynb
# Update Cell 1 to load CSV, then "Run All"

# Verify dashboard
cd ../spatiotemporal
streamlit run dashboard/streamlit_app.py
```

**Total time**: ~3-4 hours end-to-end

---

## Success Criteria

✅ Data collection completes without errors
✅ Merged CSV has ~7,840 rows covering all seasons
✅ Model training achieves >95% test accuracy
✅ Feature importance shows balanced contributions
✅ Dashboard recommendations change appropriately across seasons
✅ Winter predictions no longer favor "autumn-like" cafés

---

Ready to run! Start with `./collect_full_year_data.sh` when you have 2-3 hours available.
