# Grafana Setup for Live FinOps PoC

**Nothing to set up.** Grafana is part of `docker-compose.yml`, so `docker compose up -d`
(Step 1 of the README) starts it along with Redpanda and Postgres.

Open <http://localhost:3000> and log in with `admin` / `admin`. The
**Live FinOps PoC** dashboard is the home page.

Both of these are provisioned from files in `grafana/`, so they exist on a fresh
clone with no clicking:

| What | Defined in |
|---|---|
| Postgres datasource (uid `finops-postgres`) | `grafana/provisioning/datasources/postgres.yml` |
| Dashboard | `grafana/dashboards/finops.json` |

## The panels

**Live Cloud Burn** — cost per 10-second window, one series per resource:

```sql
SELECT
  window_end AS "time",
  resource_id AS metric,
  total_cost_usd
FROM finops_cost
WHERE $__timeFilter(window_end)
ORDER BY time ASC
```

**Anomalies Alert** — the ten most recent windows that tripped the threshold:

```sql
SELECT
  window_end AS "time",
  resource_id,
  total_cost_usd
FROM finops_cost
WHERE is_anomaly = true
  AND $__timeFilter(window_end)
ORDER BY time DESC
LIMIT 10
```

`$__timeFilter(window_end)` is a Grafana macro that expands to a `BETWEEN` against
the time picker, so each refresh reads only the visible range rather than the
whole table.

## Editing

Panels can be edited in the UI, but changes are overwritten when Grafana reloads
the provisioned file. To keep an edit, use **Dashboard settings > JSON Model**,
copy the JSON, and write it back to `grafana/dashboards/finops.json`.

## If the panels are empty

The dashboard defaults to the last 5 minutes and the Flink job only writes when
a 10-second window closes, so allow a few seconds after starting the generator
and detector. If it stays empty, check that rows are arriving:

```bash
docker compose exec postgres psql -U finops -d finops_db -c \
  'SELECT count(*), max(window_end) FROM finops_cost;'
```
