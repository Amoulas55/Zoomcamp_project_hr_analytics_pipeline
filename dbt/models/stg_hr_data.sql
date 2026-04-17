{{ config(materialized='view') }}

-- Staging model: clean raw HR data, standardize column names, cast types.
-- Generates snapshot_date since the raw dataset is a point-in-time snapshot.

WITH raw_data AS (
    SELECT * FROM {{ source('hr_raw', 'raw_hr_data') }}
)

SELECT
    CAST(Age AS INT64) AS employee_age,
    Department AS department,
    JobRole AS job_role,
    Gender AS gender,
    CAST(MonthlyIncome AS FLOAT64) AS monthly_income,
    CAST(YearsAtCompany AS INT64) AS years_at_company,
    CAST(DistanceFromHome AS INT64) AS distance_from_home,
    Education AS education_level,
    MaritalStatus AS marital_status,
    CAST(NumCompaniesWorked AS INT64) AS num_companies_worked,
    OverTime AS overtime,
    CAST(TotalWorkingYears AS INT64) AS total_working_years,
    CAST(TrainingTimesLastYear AS INT64) AS training_times_last_year,
    CAST(YearsSinceLastPromotion AS INT64) AS years_since_last_promotion,
    Attrition AS attrition_raw,
    -- The IBM dataset is a static snapshot; generate a date for partitioning
    CURRENT_DATE() AS snapshot_date
FROM raw_data
