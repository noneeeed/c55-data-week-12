-- Singular test: flag (borough, date) combinations where avg_tip_pct > 1.
-- A tip_pct > 1 means the average tip exceeded the total fare for that cell,
-- which is unusual and almost always indicates a small-sample bucket (e.g. the
-- Unknown borough) where a few high-tip outliers dominate the average.
--
-- Set this test to WARN severity by adding an inline config at the top of this
-- file (below these comments):  {{ config(severity='warn') }}
-- That keeps a few expected Unknown-borough rows from blocking `dbt build`, while
-- still surfacing them for your reports/answers.md write-up (the rubric requires
-- documenting this finding). Do NOT set a project-level test severity in
-- dbt_project.yml: that would also downgrade your not_null and
-- unique_combination primary-key tests, which you want to stay at ERROR.
--
-- The test passes (no WARN) when zero rows are returned; any returned rows are flagged.

-- TODO: write the SELECT here.
-- Query {{ ref('fct_daily_borough_stats') }} and return rows where avg_tip_pct > 1.

{{ config(severity='warn') }}
select pickup_borough, pickup_date, avg_tip_pct
from {{ ref('fct_daily_borough_stats') }}
where avg_tip_pct > 1