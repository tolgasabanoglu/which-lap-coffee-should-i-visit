-- dbt_lap/macros/dynamic_data_quality.sql

{% macro generate_missing_value_sql(source_name, table_name) %}

    {% set relation = source(source_name, table_name) %}
    {% set columns = adapter.get_columns_in_relation(relation) %}

    {% set union_sql = [] %}

    {% for column in columns %}
        {% set column_name = column.name %}

        {% set sql %}
        SELECT
            '{{ column_name }}' AS column_name,
            COUNTIF({{ column_name }} IS NULL) AS null_count,
            COUNT(1) AS total_rows,
            ROUND(COUNTIF({{ column_name }} IS NULL) * 100.0 / COUNT(1), 2) AS null_percentage
        FROM {{ relation }}
        {% endset %}

        {% do union_sql.append(sql) %}
    {% endfor %}

    {{ union_sql | join('\nUNION ALL\n') }}

{% endmacro %}


-- Separator for the second macro

{% macro generate_stats_sql(source_name, table_name) %}

    {% set relation = source(source_name, table_name) %}
    {% set columns = adapter.get_columns_in_relation(relation) %}

    SELECT
        COUNT(*) AS row_count

        {% for column in columns %}
            {# Only include statistics for numerical types #}
            {% if column.data_type in ['INT64', 'FLOAT64', 'NUMERIC', 'BIGNUMERIC'] %}
                , AVG({{ column.name }}) AS avg_{{ column.name }}
                , MIN({{ column.name }}) AS min_{{ column.name }}
                , MAX({{ column.name }}) AS max_{{ column.name }}
                , STDDEV({{ column.name }}) AS stddev_{{ column.name }}
            {% endif %}
        {% endfor %}

    FROM {{ relation }}

{% endmacro %}


{% macro generate_imputation_logic(source_name, table_name) %}

    {% set relation = source(source_name, table_name) %}
    {% set columns = adapter.get_columns_in_relation(relation) %}

    {% set numerical_cols = [] %}
    {% set categorical_cols = [] %}
    {% set all_cols = [] %}

    {% for column in columns %}
        {% set col_name = column.name %}
        {% set data_type = column.data_type | upper %}
        {% do all_cols.append(col_name) %}

        {% if data_type in ['INT64', 'FLOAT64', 'NUMERIC', 'BIGNUMERIC'] %}
            {% do numerical_cols.append(col_name) %}
        {% elif data_type in ['STRING', 'VARCHAR'] %}
            {% do categorical_cols.append(col_name) %}
        {% endif %}
    {% endfor %}

-- CTE 1: Calculate Global Imputation Statistics (Mean and Mode)
WITH imputation_stats AS (
    SELECT
        -- Use simple aggregation for numerical means
        {% for col_name in numerical_cols %}
        AVG({{ col_name }}) AS mean_{{ col_name }}{% if not loop.last or categorical_cols | length > 0 %},{% endif %}
        {% endfor %}

        -- Calculate mode for categorical features using a scalar subquery (safe from GROUP BY errors)
        {% for col_name in categorical_cols %}
        (
            SELECT t1.{{ col_name }}
            FROM {{ relation }} AS t1
            WHERE t1.{{ col_name }} IS NOT NULL
            GROUP BY 1
            ORDER BY COUNT(t1.{{ col_name }}) DESC, t1.{{ col_name }} ASC -- Tie-breaker: use ASC value
            LIMIT 1
        ) AS mode_{{ col_name }}{% if not loop.last %},{% endif %}
        {% endfor %}
        
    FROM {{ relation }}
    -- Crucial: Ensure this CTE only produces ONE ROW of statistics
    LIMIT 1
),

source_data AS (
    SELECT * FROM {{ relation }}
)

-- Final SELECT: Apply COALESCE to the source data using the stats
SELECT
    {% for col_name in all_cols %}
        {% if col_name in numerical_cols %}
            COALESCE(t1.{{ col_name }}, t2.mean_{{ col_name }}) AS {{ col_name }}
        {% elif col_name in categorical_cols %}
            COALESCE(t1.{{ col_name }}, t2.mode_{{ col_name }}) AS {{ col_name }}
        {% else %}
            t1.{{ col_name }} -- Pass through non-numerical/non-categorical columns unchanged
        {% endif %}
        {% if not loop.last %},{% endif %}
    {% endfor %}

FROM source_data t1
CROSS JOIN imputation_stats t2

{% endmacro %}
