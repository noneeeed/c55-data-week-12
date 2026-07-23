# Business Question Answers

Queries run against `dev_<your_name>.fct_daily_borough_stats`.

## Q1: Highest total `total_fare` across the whole loaded dataset

**SQL:**

```sql
-- TODO: query fct_daily_borough_stats grouped by pickup_borough, sum total_fare, order DESC
select
pickup_borough,
SUM(total_fare) as total_fares
from dev_bader.fct_daily_borough_stats
group by pickup_borough 
order by total_fares desc
```

**Result:** Manhatten 493955.62

**Interpretation:** highest total revenue per borough is manhatten

---

## Q2: Day with the highest overall `trip_count`

**SQL:**

```sql
-- TODO: query fct_daily_borough_stats grouped by pickup_date, sum trip_count, order DESC LIMIT 1
select
pickup_date,
SUM(trip_count) as total_trips
from dev_bader.fct_daily_borough_stats
group by pickup_date
order by total_trips  desc
limit 1
```

**Result:** 17-01-2024

**Interpretation:** highest trips count day is 17-01-2024

---

## Q3: Highest `avg_tip_pct` for any (borough, day) combination

**SQL:**

```sql
select *
from dev_bader.fct_daily_borough_stats
order by avg_tip_pct desc
limit 5
```

**Result:** unknown borough

**Interpretation:** shows highest average tip precentages per borough/date. any average tips precentages above 1 do show, because we didnt add where tip_pct > 1 when building mart and we used a warn assert test instead which keeps them in the data

---

## Q4: Median daily `trip_count` for Manhattan vs Brooklyn

**SQL:**

```sql
-- TODO: use percentile_cont(0.5) WITHIN GROUP (ORDER BY trip_count) filtered by borough
SELECT 
    pickup_borough,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY trip_count) AS median_daily
FROM dev_bader.fct_daily_borough_stats
WHERE pickup_borough IN ('Manhattan', 'Brooklyn')
GROUP BY pickup_borough;
```

**Result:** 248 for brooklyn and 1169.5 for manhatten

**Interpretation:** manhatten has almost 4.7 times the trip count volume as brooklyn
