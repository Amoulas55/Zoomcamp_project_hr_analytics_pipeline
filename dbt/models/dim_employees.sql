{{ config(materialized='table', cluster_by=['department']) }}

-- Dimension table: enriches employee records with income brackets
-- and tenure risk categories for dashboard filtering.

SELECT
    *,
    CASE
        WHEN monthly_income < 5000 THEN 'Entry Level'
        WHEN monthly_income BETWEEN 5000 AND 10000 THEN 'Mid Level'
        ELSE 'Senior Level'
    END AS income_bracket,
    CASE
        WHEN years_at_company <= 2 THEN 'New (0-2y)'
        WHEN years_at_company <= 5 THEN 'Growing (3-5y)'
        WHEN years_at_company <= 10 THEN 'Established (6-10y)'
        ELSE 'Veteran (10+y)'
    END AS tenure_category
FROM {{ ref('stg_hr_data') }}
