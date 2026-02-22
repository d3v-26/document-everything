# Project Type: Data Pipeline

Standard: **dbt documentation conventions** for SQL pipelines; **OpenLineage** for cross-system lineage. Both adopted industry-wide.

References:
- https://docs.getdbt.com/docs/build/documentation
- https://openlineage.io/

---

## Type-Specific Section: Pipeline

Replace `[Type-Specific Section(s)]` in the report with:

```markdown
## Pipeline

### Pipelines / DAGs

| Pipeline | Schedule | Trigger | SLA | Purpose |
|----------|---------|---------|-----|---------|
| `[name]` | `[cron or —]` | [manual/event/schedule] | [minutes] | [what it produces] |

### Tasks / Nodes

| Task | Pipeline | Upstream | Downstream | Purpose |
|------|---------|---------|-----------|---------|
| `[name]` | `[pipeline]` | `[task(s)]` | `[task(s)]` | [what it transforms] |

### Data Flow

```
[Source] → [Extract] → [raw/] → [Transform] → [processed/] → [Load] → [Destination]
```

### Data Layers

| Layer | Location | Naming Convention | Description |
|-------|---------|------------------|-------------|
| Raw / Sources | `[path]` | `src_*` | Unmodified source data |
| Staging | `[path]` | `stg_*` | Cleaned, renamed, typed |
| Intermediate | `[path]` | `int_*` | Joined, aggregated |
| Marts / Facts / Dims | `[path]` | `fct_*`, `dim_*` | Final output for consumers |

### Data Quality Tests

| Model / Table | Test | Column | Purpose |
|--------------|------|--------|---------|
| `[model]` | `unique` | `[col]` | No duplicate rows |
| `[model]` | `not_null` | `[col]` | Required field |
| `[model]` | `accepted_values` | `[col]` | Enum constraint |
```

---

## dbt Model Documentation Standard

For dbt projects, each model should be documented in `schema.yml` with these fields:

```yaml
models:
  - name: fct_customer_ltv
    description: >
      [Business purpose of the model. What question does it answer?
      Who uses it? What transformation logic is applied?]

    meta:
      owner: "[team-name]"
      maturity: "production"   # development | staging | production
      refreshed: "daily"
      contains_pii: false
      sla_hours: 4
      related_dashboards: ["[dashboard-name]"]

    columns:
      - name: customer_id
        description: "[What this column represents, units if applicable, nullability]"
        data_type: INTEGER
        tests:
          - unique
          - not_null

      - name: lifetime_value_usd
        description: >
          [Description including: what it represents, how it's calculated,
          any caveats (e.g. 'null for customers with < 90 days history')]
        data_type: FLOAT
```

When generating docs for a dbt project, produce:
- A table of all models with description, owner, maturity, and refresh schedule
- Column-level documentation for each model's key columns
- The data lineage (DAG) description — which models depend on which

---

## What to Look For

**In DAG / pipeline definitions:**
- Task dependencies (`.set_upstream()`, `>>` operator, `depends_on`) → execution order
- Schedule expressions → when and how often data flows
- `on_failure_callback` / `on_retry_callback` → failure handling strategy
- `sla` → service level agreement, document it

**In dbt models:**
- `ref()` calls → lineage; which models this depends on
- `source()` calls → raw data ingestion points; document source freshness
- Model type (`table` / `view` / `incremental`) → performance decision to document
- `is_incremental()` macro → incremental strategy, document the unique key

**In Airflow / Prefect / Luigi tasks:**
- What data source is read (SQL query, API, S3 path, Kafka topic)
- What transformation is applied
- What destination is written to
- Retry count / retry delay → known reliability issues

**In config / settings:**
- Database connection names → which warehouse/DB is used
- S3/GCS bucket paths → data storage locations
- Connection timeouts → reliability constraints

## Inferring "Why"

- Incremental dbt models → cost/performance optimization; full refresh too expensive
- `unique_key` in incremental model → idempotency requirement, can be re-run safely
- `max_active_runs=1` in Airflow → prevents parallel runs corrupting shared state
- `catchup=False` → deliberate decision not to backfill historical periods
- `retry=3, retry_delay=300` → known flaky upstream source
- Separate `raw/staging/marts` layers → reproducibility (can always reprocess from raw)
- Partitioning by date → cost optimization or data retention / regulatory requirement
- Multiple data quality tests on a column → past incident with bad data reaching consumers

## dbt Documentation Site

If the project uses dbt, note that `dbt docs generate && dbt docs serve` produces an interactive documentation site with:
- Full model DAG visualization
- Column-level lineage
- Test results
- Auto-generated from `schema.yml` descriptions

Recommend running it and linking to the generated site from `README.md`.
