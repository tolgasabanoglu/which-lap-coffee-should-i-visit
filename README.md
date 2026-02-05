# LAP Coffee Berlin: Mood-Based Café Recommender

A machine learning project that recommends LAP Coffee locations in Berlin based on your current mood and environmental conditions.

## Project Overview

This project uses Random Forest classification to predict optimal LAP Coffee locations based on environmental data and personalized mood profiles.

**The concept:** Different moods call for different environments. By mapping mood preferences to environmental features (greenness, urban activity, weather), the model recommends cafés that match your current state of mind.

## How the RFC Model Works

The recommendation system follows a 5-step pipeline from health metrics to café suggestions:

### Step 1: Health Metrics → Mood Profile Features

Your Garmin biometrics (stress, sleep, body battery, heart rate) are mapped to environmental preferences:

**Example:**
```python
# Input: Your health data
stress = 65           # High stress
sleep_hours = 6.5     # Poor sleep
net_battery = -15     # Drained energy

# Decision logic determines mood profile
if stress > 60 and sleep_hours < 7:
    mood = "green_nature"  # You need relaxation!

# Mood translates to environmental features
features = {
    "parks_count_1km": 15,      # Lots of green space
    "open_bars_count_500m": 3,  # Quiet neighborhood
    "ndvi": 0.70,                # High greenness (satellite)
    "nightlight": 20,            # Low light pollution
    "lst_celsius_1km": 12,       # Current temperature
    "precip_mm": 0               # No rain
}
```

**Available mood profiles:** `green_nature`, `cozy_indoor`, `buzz_urban`, `rainy_retreat`, `cozy_recharge`, `balanced`

### Step 2: Random Forest Classifier Prediction

The RFC model was trained on 3,648 observations across all seasons (Winter: 720, Spring: 800, Summer: 1,312, Autumn: 816) from December 2023 to November 2024. When you make a prediction:

```python
X = [[15, 3, 12, 14, 9, 0, 0.70, 20]]  # Your feature vector
probabilities = model.predict_proba(X)  # RFC with 100 decision trees
```

**How RFC works internally:**
- 100 decision trees each vote for a café based on your features
- Each tree learned patterns like: "parks=15 + ndvi=0.70 → Falckensteinstraße"
- Final prediction = voting results across all trees

**Example output:**
```python
{
    "LAP COFFEE_Falckensteinstraße": 49%,  # 49 trees voted for this
    "LAP COFFEE_Kastanienallee": 21%,      # 21 trees voted for this
    "LAP COFFEE_Akazienstraße": 15%,       # 15 trees voted for this
    "LAP COFFEE_Uhlandstraße": 8%,         # 8 trees voted for this
    # ... 12 more cafés with lower probabilities
}
```

### Step 3: Location Filtering

Cafés are filtered by distance from home (Bruchsaler Str., 10715 Berlin):

```python
max_distance_km = 10  # Default: 10km radius

cafes_nearby = [
    {"name": "Falckensteinstraße", "confidence": 49%, "distance": 3.2 km},
    {"name": "Kastanienallee", "confidence": 21%, "distance": 5.1 km},
    {"name": "Akazienstraße", "confidence": 15%, "distance": 1.8 km},
]
```

### Step 4: Balanced Scoring & Ranking

To ensure diversity and prevent always recommending the closest café:

```python
# Normalize distance score (closer = higher)
distance_score = (1 - distance_km / max_distance) * 100

# Balanced scoring: 60% model confidence + 40% proximity
balanced_score = confidence * 0.6 + distance_score * 0.4

# Add randomness for variety (±5 points)
final_score = balanced_score + random(-5, +5)
```

**Example calculation:**
```
Falckensteinstraße: 49*0.6 + 37*0.4 + 2.3 = 46.6 ← Winner!
Akazienstraße: 15*0.6 + 65*0.4 - 4.1 = 30.9
```

### Step 5: Generate Explanation

Each recommendation includes human-readable reasoning:

```python
"Your high stress level (65/100) + limited sleep (6.5hr) suggest a
'Green Nature' mood (seeking natural, restorative environment).
This café offers a surrounded by greenery (NDVI: 0.70, parks: 15),
minimal urban activity."
```

## Integration with Spatiotemporal Dashboard

The LAP Coffee model is integrated into the [Spatiotemporal Dashboard](https://github.com/tolgasabanoglu/spatiotemporal) which:
1. Fetches daily Garmin health metrics (stress, sleep, body battery, HR)
2. Calls `get_recommendations()` with your current health state
3. Displays top café recommendation with distance, mood profile, and reasoning
4. Updates daily based on your changing biometrics

**Live dashboard features:**
- Real-time weather integration (Open-Meteo API)
- Daily health trend visualizations (Plotly)
- GenAI-powered music recommendations (Gemini API)
- Coffee + song pairing based on current state

## data & features

- **LAP Coffee locations:** 15 cafés across Berlin
- **Full-year seasonal data** (~4,288 observations covering all seasons in 2024)
  - Winter (Dec 2023 - Feb 2024): ~720 observations
  - Spring (Mar - May 2024): ~800 observations
  - Summer (Jun - Aug 2024): ~1,312 observations
  - Autumn (Sep - Nov 2024): ~1,456 observations
- **Environmental features:** temperature, precipitation, NDVI (greenness), nightlight intensity
- **Neighborhood features:** parks within 1km, bars within 500m

## Model Performance

- **Algorithm:** Random Forest Classifier (with hyperparameter tuning)
- **Validation:** 5-fold cross-validation
- **Accuracy:** ~96% (test set)
- **Key finding:** Neighborhood context (parks: 34.8%, bars: 34.4%) matters more than weather (<20%) for café selection
- **Optimization:** GridSearchCV tuning for n_estimators, max_depth, min_samples_split, min_samples_leaf

## Mood Profiles

| Mood | Profile Characteristics |
|------|------------------------|
| Cozy | High parks, low bars, cold temps, low nightlight |
| Green | Maximum greenery (NDVI), high parks, low urban activity |
| Buzz | High bars, high nightlight, low greenery |

**Feature sampling:** Mood profiles use random sampling within percentile ranges, ensuring realistic values and variety across predictions.

## Enhanced Prediction System

The model now includes advanced features for more reliable recommendations:

### Confidence-Based Filtering
- **Minimum confidence threshold:** Only recommend cafes with prediction confidence above 10%
- **Confidence levels:** High (>50%), Medium (30-50%), Low (15-30%), Very Low (<15%)
- **Suitability scores:** Each recommendation includes a 0-100% suitability score

### Key Features
- **Top-N recommendations:** Get multiple cafe options ranked by suitability
- **Multi-mood predictions:** Compare recommendations across different mood profiles
- **Prediction explanations:** Understand which features drive each recommendation
- **Robust validation:** Cross-validation and hyperparameter tuning ensure reliable performance

### Usage
```python
from enhanced_predictor import EnhancedCafePredictor

# Initialize predictor
predictor = EnhancedCafePredictor(model, label_encoder, cafe_lookup_df)

# Get recommendations with confidence filtering
recommendations = predictor.predict_with_confidence(
    mood_profile_df,
    top_n=5,
    min_confidence=0.10
)

# Get summary across all moods
summary = predictor.get_mood_summary(mood_profiles)
```

## Example Predictions

| Mood | Top Recommendation | Suitability | Confidence Level |
|------|-------------------|-------------|------------------|
| Cozy | Uhlandstraße 30 | 73% | High |
| Green | Falckensteinstraße 5 | 61% | High |
| Buzz | Rosenthaler Str. 62 | 38% | Medium |

## Model Improvements

### What Was Fixed
1. **Dead code removal:** Removed unreachable code in [moods.py:243-249](prediction/moods.py#L243-L249)
2. **Data range validation:** Fixed Monte Carlo mood ranges to match actual data bounds (parks: 1-13, bars: 6-22)
3. **Cross-validation:** Added 5-fold CV to assess model robustness
4. **Hyperparameter tuning:** Implemented GridSearchCV for optimal model parameters
5. **Confidence filtering:** Added prediction confidence thresholds to prevent low-quality recommendations

### Model Interpretation
The model achieves high accuracy by learning static location signatures (parks and bars count) rather than purely dynamic mood-environment relationships. This makes it effective as a **feature-based location matcher** that maps mood profiles to cafes with similar environmental characteristics.

### Known Limitations
- High accuracy is partially due to memorizing static location features
- Model learns "which cafe has X parks and Y bars" more than "which environment suits mood Z"
- Predictions are most reliable when mood profiles fall within the training data distribution
- Weather features have lower importance (<20%) compared to neighborhood features (>60%)

## Screenshots & Documentation

### Taking Dashboard Screenshots

To document the integrated Spatiotemporal dashboard with LAP Coffee recommendations:

**1. Run the Dashboard:**
```bash
cd ~/Desktop/github/spatiotemporal
source venv/bin/activate  # If using virtual environment
streamlit run dashboard/streamlit_app.py
```

**2. Take Screenshots (macOS):**
- **Full window:** `Cmd + Shift + 4`, then press `Space`, click window
- **Selection:** `Cmd + Shift + 4`, drag to select area
- **Entire screen:** `Cmd + Shift + 3`

Screenshots are saved to `~/Desktop` by default.

**3. Organize Screenshots:**
```bash
# Create screenshots directory in project
mkdir -p docs/screenshots

# Move screenshots (example names)
mv ~/Desktop/dashboard-overview.png docs/screenshots/
mv ~/Desktop/coffee-recommendation.png docs/screenshots/
mv ~/Desktop/health-trends.png docs/screenshots/
```

**4. Add to README:**
```markdown
## Dashboard Preview

### Coffee Recommendation
![Coffee Recommendation](docs/screenshots/coffee-recommendation.png)
*ML-powered café suggestion based on current health metrics and mood profile*

### Health Trends
![Health Trends](docs/screenshots/health-trends.png)
*Daily stress, sleep, and body battery visualizations with 7-day rolling averages*

### Music Pairing
![Music Pairing](docs/screenshots/music-pairing.png)
*GenAI-generated playlist matching your current mood and weather*
```

**5. Optimize Images (Optional):**
```bash
# Install ImageMagick if needed
brew install imagemagick

# Resize large screenshots
magick docs/screenshots/*.png -resize 800x600 docs/screenshots/resized/

# Or use online tools: tinypng.com, squoosh.app
```

### Recommended Screenshots

For complete documentation, capture:
- **Main dashboard view** - Overview with all sections visible
- **Coffee recommendation card** - Showing café name, distance, mood profile, reasoning
- **Health metrics KPIs** - Current stress, sleep, battery, HR values
- **Trend charts** - Time series plots for stress, sleep trends
- **Music recommendations** - GenAI-generated playlist with song explanations
- **Info box** - Classification methodology explanation (expanded)

---

