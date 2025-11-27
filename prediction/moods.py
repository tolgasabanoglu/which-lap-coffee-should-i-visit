import pandas as pd
import numpy as np


def create_dynamic_profile(
    park_range, bar_range, lst_range, tmax_range, tmin_range,
    precip_range, ndvi_range, nightlight_range, features_to_analyze,
    seed=None
):
    """
    Creates a single synthetic profile by sampling values
    from each provided range. Returns a 1-row DataFrame.
    
    Args:
        seed: Optional random seed for reproducibility
    """
    if seed is not None:
        np.random.seed(seed)

    values = {
        'parks_count_1km': np.random.uniform(*park_range),
        'open_bars_count_500m': np.random.uniform(*bar_range),
        'lst_celsius_1km': np.random.uniform(*lst_range),
        'temp_max': np.random.uniform(*tmax_range),
        'temp_min': np.random.uniform(*tmin_range),
        'precip_mm': np.random.uniform(*precip_range),
        'ndvi': np.random.uniform(*ndvi_range),
        'nightlight': np.random.uniform(*nightlight_range),
    }

    # Keep only intended features (order preserved)
    filtered = {k: v for k, v in values.items() if k in features_to_analyze}

    return pd.DataFrame([filtered])


def get_static_mood_dataframes(features_to_analyze):
    """
    Generate fixed mood profiles with hardcoded ideal values.
    These profiles are deterministic and will always produce the same results.
    Values are chosen based on actual data ranges to represent the essence of each mood.
    """
    
    # --- Cozy (Cold & Sheltered) ---
    # Think: reading indoors on a cold day, few people around, green views, quiet neighborhood
    cozy_values = {
        'parks_count_1km': 9.0,           # High parks - peaceful residential
        'open_bars_count_500m': 7.0,      # Low bars - quiet area
        'lst_celsius_1km': 10.5,          # Cool surface temperature
        'temp_max': 11.0,                 # Cold day
        'temp_min': 5.5,                  # Chilly morning
        'precip_mm': 8.0,                 # Moderate rain adds to coziness
        'ndvi': 0.45,                     # Moderate-high greenery for nice views
        'nightlight': 20.0,               # Low light pollution - calm neighborhood
    }
    cozy_filtered = {k: v for k, v in cozy_values.items() if k in features_to_analyze}
    cozy_profile_df = pd.DataFrame([cozy_filtered])

    # --- Green (Nature Escape) ---
    # Think: park picnic, hiking day, surrounded by nature, peaceful and fresh
    green_values = {
        'parks_count_1km': 12.0,          # Maximum parks - nature everywhere
        'open_bars_count_500m': 8.0,      # Low bars - not urban core
        'lst_celsius_1km': 16.0,          # Pleasant mild temperature
        'temp_max': 19.0,                 # Nice warm day
        'temp_min': 11.0,                 # Comfortable morning
        'precip_mm': 0.3,                 # Minimal rain - perfect outdoor weather
        'ndvi': 0.70,                     # Super high greenery - lush vegetation
        'nightlight': 19.0,               # Low light - natural/suburban area
    }
    green_filtered = {k: v for k, v in green_values.items() if k in features_to_analyze}
    green_profile_df = pd.DataFrame([green_filtered])

    # --- Buzz (Urban Activity) ---
    # Think: Friday night downtown, restaurants packed, city energy, vibrant nightlife
    buzz_values = {
        'parks_count_1km': 3.0,           # Few parks - dense urban core
        'open_bars_count_500m': 20.0,     # Very high bars - entertainment district
        'lst_celsius_1km': 24.0,          # Hot urban heat island effect
        'temp_max': 25.0,                 # Warm summer evening
        'temp_min': 15.0,                 # Warm night
        'precip_mm': 0.0,                 # No rain - perfect for going out
        'ndvi': 0.10,                     # Very low greenery - concrete jungle
        'nightlight': 65.0,               # High light pollution - bright city lights
    }
    buzz_filtered = {k: v for k, v in buzz_values.items() if k in features_to_analyze}
    buzz_profile_df = pd.DataFrame([buzz_filtered])

    # --- Rainy Retreat ---
    # Think: cozy café during downpour, staying in with tea, peaceful rain sounds
    rainy_values = {
        'parks_count_1km': 6.0,           # Some parks but staying indoors
        'open_bars_count_500m': 9.0,      # Moderate bars - mixed neighborhood
        'lst_celsius_1km': 13.0,          # Cool and damp
        'temp_max': 14.0,                 # Cool rainy day
        'temp_min': 7.0,                  # Chilly and wet
        'precip_mm': 18.0,                # Heavy rain - proper downpour
        'ndvi': 0.35,                     # Moderate greenery - urban but with green spaces
        'nightlight': 22.0,               # Low-moderate light - quiet evening
    }
    rainy_filtered = {k: v for k, v in rainy_values.items() if k in features_to_analyze}
    rainy_profile_df = pd.DataFrame([rainy_filtered])

    # --- Random (Balanced) ---
    # Think: average day, nothing extreme, typical mixed neighborhood
    random_values = {
        'parks_count_1km': 7.0,           # Median park access
        'open_bars_count_500m': 10.0,     # Median bar density
        'lst_celsius_1km': 16.5,          # Median temperature
        'temp_max': 16.6,                 # Median day temp
        'temp_min': 9.0,                  # Median night temp
        'precip_mm': 0.6,                 # Median precipitation
        'ndvi': 0.19,                     # Median greenery
        'nightlight': 23.7,               # Median urban lighting
    }
    random_filtered = {k: v for k, v in random_values.items() if k in features_to_analyze}
    random_profile_df = pd.DataFrame([random_filtered])

    return {
        'Cozy (Cold & Sheltered)': cozy_profile_df,
        'Green (Nature Escape)': green_profile_df,
        'Buzz (Urban Activity)': buzz_profile_df,
        'Rainy Retreat': rainy_profile_df,
        'Random (Balanced Profile)': random_profile_df
    }


def get_random_mood_dataframes(features_to_analyze, seed=None):
    """
    Generate random mood profiles by sampling uniformly within the full data range.
    Each call produces different values (unless seed is provided).
    
    Args:
        features_to_analyze: List of features to include
        seed: Optional random seed for reproducibility
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Data ranges from your actual dataset
    ranges = {
        'parks_count_1km': (1.0, 13.0),
        'open_bars_count_500m': (6.0, 22.0),
        'lst_celsius_1km': (-4.75, 31.85),
        'temp_max': (-1.30, 30.30),
        'temp_min': (-8.10, 17.20),
        'precip_mm': (0.0, 26.50),
        'ndvi': (-0.02, 0.76),
        'nightlight': (12.82, 86.21),
    }
    
    moods = ['Cozy', 'Green', 'Buzz', 'Rainy', 'Random']
    mood_dfs = {}
    
    for mood in moods:
        values = {}
        for feature in features_to_analyze:
            if feature in ranges:
                min_val, max_val = ranges[feature]
                values[feature] = np.random.uniform(min_val, max_val)
        
        mood_dfs[f'{mood} (Random)'] = pd.DataFrame([values])
    
    return mood_dfs


def get_monte_carlo_mood_ensemble(features_to_analyze, n_samples=100, seed=None):
    """
    Generate Monte Carlo ensemble of mood profiles.
    Returns multiple samples per mood for uncertainty quantification.
    
    Args:
        features_to_analyze: List of features to include
        n_samples: Number of samples per mood (default 100)
        seed: Optional random seed for reproducibility
        
    Returns:
        Dictionary with mood names as keys, DataFrames with n_samples rows as values
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Define characteristic ranges for each mood (tighter than full data range)
    mood_ranges = {
        'Cozy (Cold & Sheltered)': {
            'parks_count_1km': (7.0, 11.0),
            'open_bars_count_500m': (3.0, 5.0),
            'lst_celsius_1km': (8.0, 14.0),
            'temp_max': (9.0, 14.0),
            'temp_min': (-3.0, 2.0),
            'precip_mm': (5.0, 12.0),
            'ndvi': (0.35, 0.55),
            'nightlight': (15.0, 25.0),
        },
        'Green (Nature Escape)': {
            'parks_count_1km': (15.0, 20.0),
            'open_bars_count_500m': (0.0, 2.0),
            'lst_celsius_1km': (14.0, 19.0),
            'temp_max': (17.0, 22.0),
            'temp_min': (9.0, 13.0),
            'precip_mm': (0.0, 2.0),
            'ndvi': (0.70, 0.9),
            'nightlight': (12.00, 15.0),
        },
        'Buzz (Urban Activity)': {
            'parks_count_1km': (1.0, 5.0),
            'open_bars_count_500m': (16.0, 22.0),
            'lst_celsius_1km': (20.0, 31.85),
            'temp_max': (22.0, 30.30),
            'temp_min': (13.0, 17.20),
            'precip_mm': (0.0, 1.5),
            'ndvi': (-0.02, 0.1),
            'nightlight': (50.0, 86.21),
        },
        'Random (Balanced Profile)': {
            'parks_count_1km': (1.0, 13.0),
            'open_bars_count_500m': (6.0, 22.0),
            'lst_celsius_1km': (-4.75, 31.85),
            'temp_max': (-1.30, 30.30),
            'temp_min': (-8.10, 17.20),
            'precip_mm': (0.0, 26.50),
            'ndvi': (-0.02, 0.76),
            'nightlight': (12.82, 86.21),
        },
    }
    
    mood_ensembles = {}
    
    for mood_name, ranges in mood_ranges.items():
        samples = []
        for _ in range(n_samples):
            values = {}
            for feature in features_to_analyze:
                if feature in ranges:
                    min_val, max_val = ranges[feature]
                    values[feature] = np.random.uniform(min_val, max_val)
            samples.append(values)
        
        mood_ensembles[mood_name] = pd.DataFrame(samples)
    
    return mood_ensembles

    return {
        'Cozy (Cold & Sheltered)': cozy_profile_df,
        'Green (Nature Escape)': green_profile_df,
        'Buzz (Urban Activity)': buzz_profile_df,
        'Rainy Retreat': rainy_profile_df,
        'Random (Balanced Profile)': random_profile_df
    }


def get_dynamic_mood_dataframes(F_MIN, F_P25, F_P50, F_P75, F_MAX, features_to_analyze, seed=None):
    """
    Generate synthetic mood profiles for distinct moods with optional reproducibility.
    
    Args:
        seed: Optional random seed for reproducible random sampling
    """

    # --- Cozy (Cold & Sheltered) ---
    cozy_profile_df = create_dynamic_profile(
        park_range=[F_P50['parks_count_1km'], F_P75['parks_count_1km']],
        bar_range=[F_MIN['open_bars_count_500m'], F_P25['open_bars_count_500m']],
        lst_range=[F_MIN['lst_celsius_1km'], F_P25['lst_celsius_1km']],
        tmax_range=[F_P25['temp_max'], F_P50['temp_max']],
        tmin_range=[F_P25['temp_min'], F_P50['temp_min']],
        precip_range=[F_P50['precip_mm'], F_P75['precip_mm']],
        ndvi_range=[F_P50['ndvi'], F_P75['ndvi']],
        nightlight_range=[F_MIN['nightlight'], F_P25['nightlight']],
        features_to_analyze=features_to_analyze,
        seed=seed
    )

    # --- Green (Nature Escape) ---
    green_profile_df = create_dynamic_profile(
        park_range=[F_P75['parks_count_1km'], F_MAX['parks_count_1km']],
        bar_range=[F_P25['open_bars_count_500m'], F_P50['open_bars_count_500m']],
        lst_range=[F_MIN['lst_celsius_1km'], F_P50['lst_celsius_1km']],
        tmax_range=[F_P50['temp_max'], F_P75['temp_max']],
        tmin_range=[F_P50['temp_min'], F_P75['temp_min']],
        precip_range=[F_P25['precip_mm'], F_P50['precip_mm']],
        ndvi_range=[F_P75['ndvi'], F_MAX['ndvi']],
        nightlight_range=[F_MIN['nightlight'], F_P25['nightlight']],
        features_to_analyze=features_to_analyze,
        seed=seed+1 if seed else None
    )

    # --- Buzz (Urban Activity) ---
    buzz_profile_df = create_dynamic_profile(
        park_range=[F_P25['parks_count_1km'], F_P50['parks_count_1km']],
        bar_range=[F_P75['open_bars_count_500m'], F_MAX['open_bars_count_500m']],
        lst_range=[F_P75['lst_celsius_1km'], F_MAX['lst_celsius_1km']],
        tmax_range=[F_P75['temp_max'], F_MAX['temp_max']],
        tmin_range=[F_P50['temp_min'], F_P75['temp_min']],
        precip_range=[F_P25['precip_mm'], F_P50['precip_mm']],
        ndvi_range=[F_MIN['ndvi'], F_P25['ndvi']],
        nightlight_range=[F_P75['nightlight'], F_MAX['nightlight']],
        features_to_analyze=features_to_analyze,
        seed=seed+2 if seed else None
    )

    # --- Random (Balanced) ---
    random_profile_df = create_dynamic_profile(
        park_range=[F_P50['parks_count_1km']*0.95, F_P50['parks_count_1km']*1.05],
        bar_range=[F_P50['open_bars_count_500m']*0.95, F_P50['open_bars_count_500m']*1.05],
        lst_range=[F_P50['lst_celsius_1km']*0.95, F_P50['lst_celsius_1km']*1.05],
        tmax_range=[F_P50['temp_max']*0.95, F_P50['temp_max']*1.05],
        tmin_range=[F_P50['temp_min']*0.95, F_P50['temp_min']*1.05],
        precip_range=[F_P50['precip_mm']*0.95, F_P50['precip_mm']*1.05],
        ndvi_range=[F_P50['ndvi']*0.95, F_P50['ndvi']*1.05],
        nightlight_range=[F_P50['nightlight']*0.95, F_P50['nightlight']*1.05],
        features_to_analyze=features_to_analyze,
        seed=seed+4 if seed else None
    )

    return {
        'Cozy (Cold & Sheltered)': cozy_profile_df,
        'Green (Nature Escape)': green_profile_df,
        'Buzz (Urban Activity)': buzz_profile_df,
        'Random (Balanced Profile)': random_profile_df
    }