-- dbt_lap/models/marts/data_cleansing/lap_data_imputed.sql
-- This model dynamically identifies numerical (INT/FLOAT) and categorical (STRING)
-- columns and imputes missing values using the mean or mode.

{{ generate_imputation_logic('which_lap_data', 'lap_locations_final_merged') }}
