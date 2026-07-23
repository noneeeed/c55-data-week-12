# Assignment report

<!-- Replace every TODO. Keep it short: a few sentences per section. -->

## Schedule choice and reason

{{ds}}  logical date. because choosing timenow i couldnt manually trigger runs on airflow choosing a specifec past date.

## Task dependency graph

ingest_taxi_month() >> dbt_run >> dbt_test
chain matter because its linear and not exponential it follows that exact order in one line.


## dbt project used
Week 10 project

## One debugging case I resolved

placed dbt project in the wrong place and project couldnt find them.
found out from the logs in the dbt run.
Task failed with exceptionAirflowException: Bash command failed. The command returned a non-zero exit code 2.



## deploy proof
https://github.com/lassebenni/c55-shared-airflow/pull/6
image is in images folder;
![Shared deploy](/images/deploy.png)







row count after and before double backfill is the same.

SELECT to_char(lpep_pickup_datetime, 'YYYY-MM') AS month, count(*)
FROM airflow_bader.raw_trips
GROUP BY 1 ORDER BY



month  |count|
-------+-----+
2008-12|    2|
2009-01|    2|
2023-12|    4|
2024-01|56555|
2024-02|53578|
2024-03|57451|
2024-04|56472|
2024-05|61007|
2024-06|54736|
2024-07|51811|
2024-08|  125|