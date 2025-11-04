# --- dynamic_profiles.py ---
import numpy as np
import pandas as pd


def create_dynamic_profile(
    park_range, bar_range, lst_range, tmax_range, tmin_range,
    precip_range, ndvi_range, nightlight_range, features_to_analyze
):
    """
    Creates a single-row DataFrame with features sampled randomly within the given ranges.

    Args:
        Each *_range is a list or tuple [low, high].
        features_to_analyze: List of feature names (must match training model features).

    Returns:
        pd.DataFrame: A single-row DataFrame representing the synthetic mood profile.
    """
    data = [[
        np.random.uniform(*park_range),
        np.random.uniform(*bar_range),
        np.random.uniform(*lst_range),
        np.random.uniform(*tmax_range),
        np.random.uniform(*tmin_range),
        np.random.uniform(*precip_range),
        np.random.uniform(*ndvi_range),
        np.random.uniform(*nightlight_range),
    ]]
    return pd.DataFrame(data, columns=features_to_analyze)


def get_dynamic_mood_dataframes(F_MIN, F_P25, F_P50, F_P75, F_MAX, features_to_analyze):
    """
    Generates dynamic synthetic DataFrames representing ideal mood profiles.
    Considers air and land surface temperature, vegetation, light, precipitation, and activity.

    Args:
        F_MIN, F_P25, F_P50, F_P75, F_MAX: Series of feature percentiles.
        features_to_analyze: List of model features (must match RFC inputs).

    Returns:
        dict: {mood_label: profile_dataframe}
    """

    # ☕ COZY (Cold & Sheltered)
    cozy_profile_df = create_dynamic_profile(
        park_range=[F_P75['parks_count_1km'], F_MAX['parks_count_1km']],
        bar_range=[F_MIN['open_bars_count_500m'], F_P25['open_bars_count_500m']],
        lst_range=[F_MIN['lst_celsius_1km'], F_P25['lst_celsius_1km']],  # colder surface
        tmax_range=[F_P25['temp_max'], F_P50['temp_max']],
        tmin_range=[F_MIN['temp_min'], F_P25['temp_min']],
        precip_range=[F_MIN['precip_mm'], F_MIN['precip_mm'] + 0.1],
        ndvi_range=[F_P25['ndvi'], F_P50['ndvi']],
        nightlight_range=[F_MIN['nightlight'], F_P25['nightlight']],
        features_to_analyze=features_to_analyze
    )

    # 🌿 GREEN (Nature Escape)
    green_profile_df = create_dynamic_profile(
        park_range=[F_P75['parks_count_1km'], F_MAX['parks_count_1km']],
        bar_range=[F_MIN['open_bars_count_500m'], F_P25['open_bars_count_500m']],
        lst_range=[F_MIN['lst_celsius_1km'], F_P50['lst_celsius_1km']],  # cooler due to vegetation
        tmax_range=[F_P50['temp_max'], F_P75['temp_max']],
        tmin_range=[F_P25['temp_min'], F_P50['temp_min']],
        precip_range=[F_MIN['precip_mm'], F_P25['precip_mm']],
        ndvi_range=[F_P75['ndvi'], F_MAX['ndvi']],  # high greenness
        nightlight_range=[F_MIN['nightlight'], F_P25['nightlight']],
        features_to_analyze=features_to_analyze
    )

    # 🥂 BUZZ (Urban Activity)
    buzz_profile_df = create_dynamic_profile(
        park_range=[F_MIN['parks_count_1km'], F_P25['parks_count_1km']],
        bar_range=[F_P75['open_bars_count_500m'], F_MAX['open_bars_count_500m']],
        lst_range=[F_P75['lst_celsius_1km'], F_MAX['lst_celsius_1km']],  # hotter surface (urban)
        tmax_range=[F_P75['temp_max'], F_MAX['temp_max']],
        tmin_range=[F_P50['temp_min'], F_P75['temp_min']],
        precip_range=[F_P25['precip_mm'], F_P75['precip_mm']],  # some rain ok
        ndvi_range=[F_MIN['ndvi'], F_P25['ndvi']],
        nightlight_range=[F_P75['nightlight'], F_MAX['nightlight']],
        features_to_analyze=features_to_analyze
    )

    # 🛋️ LAZY (High Comfort)
    lazy_profile_df = create_dynamic_profile(
        park_range=[F_P25['parks_count_1km'], F_P75['parks_count_1km']],
        bar_range=[F_P25['open_bars_count_500m'], F_P75['open_bars_count_500m']],
        lst_range=[F_P25['lst_celsius_1km'], F_P50['lst_celsius_1km']],  # moderate surface temp
        tmax_range=[F_P25['temp_max'], F_P75['temp_max']],
        tmin_range=[F_P25['temp_min'], F_P75['temp_min']],
        precip_range=[F_MIN['precip_mm'], F_MIN['precip_mm'] + 0.1],
        ndvi_range=[F_P25['ndvi'], F_P75['ndvi']],
        nightlight_range=[F_P25['nightlight'], F_P50['nightlight']],
        features_to_analyze=features_to_analyze
    )

    # ☀️ FOCUSED (Quiet Productivity)
    focused_profile_df = create_dynamic_profile(
        park_range=[F_P50['parks_count_1km'], F_P75['parks_count_1km']],
        bar_range=[F_MIN['open_bars_count_500m'], F_P25['open_bars_count_500m']],
        lst_range=[F_P25['lst_celsius_1km'], F_P50['lst_celsius_1km']],  # not too hot, not too cold
        tmax_range=[F_P50['temp_max'], F_P75['temp_max']],
        tmin_range=[F_P25['temp_min'], F_P50['temp_min']],
        precip_range=[F_MIN['precip_mm'], F_P25['precip_mm']],
        ndvi_range=[F_P50['ndvi'], F_P75['ndvi']],
        nightlight_range=[F_P25['nightlight'], F_P50['nightlight']],
        features_to_analyze=features_to_analyze
    )

    # 🌆 NIGHTLIFE (Evening Energy)
    nightlife_profile_df = create_dynamic_profile(
        park_range=[F_MIN['parks_count_1km'], F_P25['parks_count_1km']],
        bar_range=[F_P75['open_bars_count_500m'], F_MAX['open_bars_count_500m']],
        lst_range=[F_P75['lst_celsius_1km'], F_MAX['lst_celsius_1km']],  # heat island
        tmax_range=[F_P75['temp_max'], F_MAX['temp_max']],
        tmin_range=[F_P50['temp_min'], F_P75['temp_min']],
        precip_range=[F_MIN['precip_mm'], F_P25['precip_mm']],
        ndvi_range=[F_MIN['ndvi'], F_P25['ndvi']],
        nightlight_range=[F_P75['nightlight'], F_MAX['nightlight']],  # strong night energy
        features_to_analyze=features_to_analyze
    )

    # 🌧️ RAINY-DAY COMFORT
    rainy_profile_df = create_dynamic_profile(
        park_range=[F_P25['parks_count_1km'], F_P50['parks_count_1km']],
        bar_range=[F_MIN['open_bars_count_500m'], F_P25['open_bars_count_500m']],
        lst_range=[F_MIN['lst_celsius_1km'], F_P25['lst_celsius_1km']],  # cooler ground
        tmax_range=[F_MIN['temp_max'], F_P25['temp_max']],
        tmin_range=[F_MIN['temp_min'], F_P25['temp_min']],
        precip_range=[F_P75['precip_mm'], F_MAX['precip_mm']],  # heavy rain
        ndvi_range=[F_P25['ndvi'], F_P50['ndvi']],
        nightlight_range=[F_P50['nightlight'], F_P75['nightlight']],
        features_to_analyze=features_to_analyze
    )

    # 🎲 RANDOM (Balanced Profile)
    random_profile_df = create_dynamic_profile(
        park_range=[F_P50['parks_count_1km'] * 0.9, F_P50['parks_count_1km'] * 1.1],
        bar_range=[F_P50['open_bars_count_500m'] * 0.9, F_P50['open_bars_count_500m'] * 1.1],
        lst_range=[F_P50['lst_celsius_1km'] * 0.9, F_P50['lst_celsius_1km'] * 1.1],
        tmax_range=[F_P50['temp_max'] * 0.9, F_P50['temp_max'] * 1.1],
        tmin_range=[F_P50['temp_min'] * 0.9, F_P50['temp_min'] * 1.1],
        precip_range=[F_P50['precip_mm'] * 0.9, F_P50['precip_mm'] * 1.1],
        ndvi_range=[F_P50['ndvi'] * 0.9, F_P50['ndvi'] * 1.1],
        nightlight_range=[F_P50['nightlight'] * 0.9, F_P50['nightlight'] * 1.1],
        features_to_analyze=features_to_analyze
    )

    return {
        '☕ Cozy (Cold & Sheltered)': cozy_profile_df,
        '🌿 Green (Nature Escape)': green_profile_df,
        '🥂 Buzz (Urban Activity)': buzz_profile_df,
        '🛋️ Lazy (High Comfort)': lazy_profile_df,
        '☀️ Focused (Quiet Productivity)': focused_profile_df,
        '🌆 Nightlife (Evening Energy)': nightlife_profile_df,
        '🌧️ Rainy-Day Comfort': rainy_profile_df,
        '🎲 Random (Balanced Profile)': random_profile_df
    }
