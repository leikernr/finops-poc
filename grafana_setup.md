# Grafana Setup for Live FinOps PoC

Since you already have Grafana running at `http://localhost:3000`, follow these steps to visualize the data.

## 1. Add Postgres as a Data Source

1. Open Grafana and go to **Connections > Data Sources**.
2. Click **Add new data source** and search for **PostgreSQL**.
3. Configure with the following settings:
   - **Host:** `localhost:5432` (or `host.docker.internal:5432` depending on your network)
   - **Database:** `finops_db`
   - **User:** `finops`
   - **Password:** `finops_password`
   - **TLS/SSL Mode:** `disable`
4. Click **Save & Test**.

## 2. Create the "Live Cloud Burn" Dashboard

1. Go to **Dashboards** and click **New > New Dashboard > Add visualization**.
2. Select your PostgreSQL data source.
3. Switch the query editor to **Code** (SQL mode) and enter the following query:

```sql
SELECT
  window_end AS "time",
  resource_id,
  total_cost_usd
FROM finops_cost
ORDER BY time ASC
```

4. Format as **Time series**. This will show the cost of each resource over time.

## 3. Create the "Anomalies Alert" Panel

1. Add another panel to the dashboard.
2. Select PostgreSQL data source and enter this query:

```sql
SELECT
  window_end AS "time",
  resource_id,
  total_cost_usd
FROM finops_cost
WHERE is_anomaly = true
ORDER BY time ASC
```

3. Change the visualization type to **Stat** or **Table** to clearly see any resource that has spiked and triggered the anomaly alert.
