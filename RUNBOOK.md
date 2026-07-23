# RUNBOOK — bader_taxi_pipeline

**DAG ID:** `bader_taxi_pipeline`
**Tags:** `student:bader`, `taxi`, `week12`
**Airflow UI base URL:** `http://c55-data-week-12.localhost:6563`

This document is written so that another student can operate this DAG end‑to‑end
without reading the Python source. Every step is a command to run or a click
to make — no background theory.

---

## 0. Prerequisites (one-time setup)

- Astro CLI installed and working (`astro version`)
- Azure CLI installed (`az version`)
- Access to the Azure subscription/project this course uses
- This repo cloned locally, with your terminal `cd`'d into the project folder

---

## 1. How to trigger the DAG manually

1. **Start the local Airflow environment**
   ```bash
   astro dev start
   ```
   Wait until the terminal reports the webserver and scheduler are up.

2. **Authenticate with Azure**
   ```bash
   az login
   ```
   This opens a browser window — log in with your course/organization account.
   Without this step, the next command (fetching the Postgres connection
   string) will fail with an authentication error.

3. **Fetch the Postgres connection string (`PG_URL`)**
   ```bash
   export PG_URL=$(az keyvault secret show \
     --name pg-connection-string \
     --vault-name <your-vault-name> \
     --query value -o tsv)
   ```
   > ⚠️ Replace `<your-vault-name>` (and the secret name if different) with
   > the actual Key Vault used in this course. Ask your instructor/team if
   > you don't know it — this is the one value in this runbook that depends
   > on your specific environment.

4. **Register the connection in Airflow**
   ```bash
   astro dev run connections add azure_pg --conn-uri "$PG_URL"
   ```
   This tells Airflow how to reach the Azure Postgres database under the
   connection ID `azure_pg`, which the DAG's tasks reference internally.

5. **Open the Airflow UI**
   Navigate your browser to:
   ```
   http://c55-data-week-12.localhost:6563/dags?tags=student%3Abader
   ```
   You can also filter by the `taxi` or `week12` tags using the same
   pattern (`?tags=taxi`, `?tags=week12`), or combine them in the UI's tag
   filter bar.

6. **Find and trigger the DAG**
   - Locate `bader_taxi_pipeline` in the DAG list.
   - Hover over the row — a **Trigger** (▶) button appears on the right side
     of the row.
   - Click **Trigger DAG** (the play icon), then confirm in the dialog that
     pops up (leave config JSON empty unless you specifically need to pass
     parameters).
   - The DAG run will appear at the top of the run history with a status of
     `running`.

---

## 2. How to run a backfill

Use this when you need to (re)process a historical date range instead of
triggering a single run.

```bash
astro dev run backfill create \
  --dag-id bader_taxi_pipeline \
  --from-date 2024-01-01 \
  --to-date 2024-03-31 \
  --max-active-runs 1
```

Notes:
- `--from-date` / `--to-date` define the inclusive date range to backfill.
  Adjust these to the range you actually need.
- `--max-active-runs 1` forces the backfill to run one date at a time. This
  is slower but avoids overloading the shared Postgres database — don't
  raise it unless you know the DB can handle concurrent runs.
- You still need `az login` and the `azure_pg` connection (steps 2–4 above)
  set up before running a backfill.

---

## 3. How to inspect task logs

1. Go to the DAG's run history:
   ```  http://c55-data-week-12.localhost:6563/dags   ```
2. Click on `bader_taxi_pipeline` to open the DAG detail view.
or directly to ``` http://c55-data-week-12.localhost:6563/dags/bader_taxi_pipeline ```
3. Click on the specific **DAG run** (identified by its execution date/run
   ID) you want to inspect.
4. In the Grid or Graph view, click on the individual **task instance**
   (the colored square/box for that task).
5. In the panel that opens, click **Logs**. This shows the full stdout/
   stderr for that task's execution, including tracebacks on failure.

If the UI is unreachable, you can also stream logs directly from the CLI:
```bash
astro dev logs --scheduler
astro dev logs --webserver
```

---

## 4. Top 3 likely failures and first response

| # | Symptom | First check / fix |
|---|---------|--------------------|
| 1 | Error: error building, (re)creating or starting project containers: Error response from daemon: ports are not available: exposing port TCP 127.0.0.1:5432 -> 127.0.0.1:0: /forwards/expose returned unexpected status: 500: `astro config set postgres.port 5433`, then `astro dev start` again. | [5433 port can be changed if busy]
| 2 | `az`/Azure calls fail with `Please run 'az login'` or a 401/403 error when fetching `PG_URL` | You forgot to authenticate before fetching config. Run `az login`, confirm with `az account show`, then retry step 3. |
| 3 | ask fails with `Connection azure_pg not found` / DB connection error | You forgot to register the connection. Re-run steps 3–4 above: fetch `PG_URL` (requires `az login` first), then `astro dev run connections add azure_pg --conn-uri "$PG_URL"`. |  [Make sure the PGURL is populated from UI by clicking left panel Admin> connections  OR http://c55-data-week-12.localhost:6563/connections]
T
---

## 5. Quick reference

```bash
# Full manual trigger sequence, start to finish
astro dev start
az login
export PG_URL=$(az keyvault secret show --name pg-connection-string --vault-name <your-vault-name> --query value -o tsv)
astro dev run connections add azure_pg --conn-uri "$PG_URL"
# then open http://c55-data-week-12.localhost:6563/dags/bader_taxi_pipeline and trigger via the UI
```
