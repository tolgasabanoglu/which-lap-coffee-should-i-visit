# LAP Coffee Berlin: Mood-Based Café Recommender

A machine learning project that recommends LAP Coffee locations in Berlin based on your current mood and environmental conditions.

## Project Overview

This project uses Random Forest classification to predict optimal LAP Coffee locations based on environmental data and personalized mood profiles.

**The concept:** Different moods call for different environments. By mapping mood preferences to environmental features (greenness, urban activity, weather), the model recommends cafés that match your current state of mind.

## Data & Features

- **LAP Coffee locations** across Berlin
- **Multi season autumn data** 
- **Environmental features:** Temperature, precipitation, NDVI (greenness), nightlight intensity
- **Neighborhood features:** Parks within 500m, bars within 500m

## Model Performance

- **Algorithm:** Random Forest Classifier
- **Accuracy:** 96%
- **Key finding:** Neighborhood context (parks: 34.8%, bars: 34.4%) matters more than weather (<20%) for café selection

## Mood Profiles

| Mood | Profile Characteristics |
|------|------------------------|
| ☕ Cozy | High parks, low bars, cold temps, low nightlight |
| 🌿 Green | Maximum greenery (NDVI), high parks, low urban activity |
| 🥂 Buzz | High bars, high nightlight, low greenery |

**Feature sampling:** Mood profiles use random sampling within percentile ranges, ensuring realistic values and variety across predictions.

## Example Predictions

| Mood | Top Recommendation | Confidence |
|------|-------------------|------------|
| 🛋️ Lazy | Uhlandstraße 30 | 73% |
| 🌿 Green | Falckensteinstraße 5 | 61% |
| 🥂 Buzz | Rosenthaler Str. 62 | 38% |

## Tech Stack

- Python 3.x
- scikit-learn
- pandas, numpy
- Geospatial data sources

---

