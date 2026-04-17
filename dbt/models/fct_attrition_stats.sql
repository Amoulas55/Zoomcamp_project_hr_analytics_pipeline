{{
  config(
    materialized='table',
    partition_by={
      "field": "snapshot_date",
      "data_type": "date",
      "granularity": "day"
    },
    cluster_by=['department']
  )
}}

-- Fact table: core attrition metrics with binary flag for BI dashboards.
-- Partitioned by snapshot_date (daily) for efficient time-range queries.
-- Clustered by department since dashboards filter heavily on department.

SELECT
    *,
    CASE
        WHEN CAST(attrition_raw AS STRING) = 'Yes' OR CAST(attrition_raw AS STRING) = 'true' THEN 1
        ELSE 0
    END AS attrition_flag
FROM {{ ref('stg_hr_data') }}
