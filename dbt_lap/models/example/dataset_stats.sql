-- dbt_lap/models/marts/data_quality/dataset_stats.sql
-- This model now only calls the macro defined in the macros/ directory.
{{ config(
    materialized='ephemeral'
) }}

{{ generate_stats_sql('which_lap_data', 'lap_locations_final_merged') }}