{{ config(
    materialized='ephemeral'
) }}

{{ generate_missing_value_sql('which_lap_data', 'lap_locations_final_merged') }}