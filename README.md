# LAP Coffee Berlin: Mood-Based Café Recommender

A machine learning project that recommends LAP Coffee locations in Berlin based on your current mood and environmental conditions.

## Project Overview

This project uses Random Forest classification to predict optimal LAP Coffee locations based on environmental data and personalized mood profiles.

**The concept:** Different moods call for different environments. By mapping mood preferences to environmental features (greenness, urban activity, weather), the model recommends cafés that match your current state of mind.

## data & features

- **LAP Coffee locations** across Berlin
- **Autumn season data** (3,440 observations from October-November 2024)
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

---

