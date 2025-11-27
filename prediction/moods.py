def get_dynamic_mood_dataframes(F_MIN, F_P25, F_P50, F_P75, F_MAX, features_to_analyze):
    """
    Generate synthetic mood profiles for distinct moods.
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
        features_to_analyze=features_to_analyze
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
        features_to_analyze=features_to_analyze
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
        features_to_analyze=features_to_analyze
    )

    # --- Rainy Retreat ---
    rainy_profile_df = create_dynamic_profile(
        park_range=[F_P50['parks_count_1km'], F_P75['parks_count_1km']],
        bar_range=[F_MIN['open_bars_count_500m'], F_P25['open_bars_count_500m']],
        lst_range=[F_MIN['lst_celsius_1km'], F_P50['lst_celsius_1km']],
        tmax_range=[F_P25['temp_max'], F_P50['temp_max']],
        tmin_range=[F_P25['temp_min'], F_P50['temp_min']],
        precip_range=[F_P75['precip_mm'], F_MAX['precip_mm']],  # high precipitation
        ndvi_range=[F_P50['ndvi'], F_P75['ndvi']],
        nightlight_range=[F_MIN['nightlight'], F_P25['nightlight']],
        features_to_analyze=features_to_analyze
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
        features_to_analyze=features_to_analyze
    )

    return {
        'Cozy (Cold & Sheltered)': cozy_profile_df,
        'Green (Nature Escape)': green_profile_df,
        'Buzz (Urban Activity)': buzz_profile_df,
        'Rainy Retreat': rainy_profile_df,
        'Random (Balanced Profile)': random_profile_df
    }
