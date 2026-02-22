# Project Type: Data Pipeline

Guidance for documenting data pipelines, ETL processes, and workflow orchestration (Airflow, Prefect, dbt, Kedro, Luigi, etc.).

## Key Files to Read First

1. DAG / flow / pipeline definition files
2. Task / operator / transform files
3. Config files (`airflow.cfg`, `prefect.yaml`, `dbt_project.yml`, `kedro.yml`)
4. `data/` directory structure — reveals data layers (raw, intermediate, processed)
5. `requirements.txt` / `pyproject.toml` — reveals orchestrator and processing libraries

## Type-Specific Section: Pipeline

Replace the `[Type-Specific Section(s)]` placeholder in the report with:

```markdown
## Pipeline

### Pipelines / DAGs

| Pipeline | Schedule | Trigger | Purpose |
|----------|---------|---------|---------|
| `[name]` | `[cron or —]` | [manual/event/schedule] | [what it produces] |

### Tasks / Steps

| Task | Pipeline | Upstream | Downstream | Purpose |
|------|---------|---------|-----------|---------|
| `[name]` | `[pipeline]` | `[task(s)]` | `[task(s)]` | [what it does] |

### Data Flow

```
[Source] → [Extract task] → [raw/] → [Transform task] → [processed/] → [Load task] → [Destination]
```

### Data Layers

| Layer | Location | Description |
|-------|---------|-------------|
| Raw | `[path]` | [unmodified source data] |
| Intermediate | `[path]` | [cleaned / joined] |
| Processed | `[path]` | [final output for consumers] |
```

## What to Look For

**In DAG / pipeline definitions:**
- Task dependencies (`.set_upstream()`, `>>` operators, `depends_on`) = the execution order
- Schedule expressions = when and how often data flows
- `on_failure_callback` = what happens when things break

**In task/operator files:**
- What data source is read (database query, API, file, S3 path)
- What transformation is applied
- What destination is written to
- Retry settings = known reliability issues with a source/destination

**In dbt models:**
- Model type (table/view/incremental) = performance decision
- `ref()` calls = lineage — which models this depends on
- `source()` calls = raw data ingestion points
- Tests in `schema.yml` = data quality contracts

**In Kedro:**
- `catalog.yml` = the data assets and their storage locations
- `pipeline.py` = the node graph

## Inferring "Why"

- Incremental models (dbt) or `max_active_runs=1` (Airflow) = performance/cost decisions
- Multiple retry attempts on a task = unreliable upstream source
- Data quality tests = past incidents with bad data reaching consumers
- Separate raw/intermediate/processed layers = reproducibility requirement (can always reprocess from raw)
- `catchup=False` (Airflow) = deliberate decision not to backfill historical runs
- Partitioning by date = cost optimization or regulatory data retention requirement

## Common Architectural Decisions to Document

- Why certain tasks are parallelized vs sequential (cost vs complexity)
- Why data is stored at each layer (reproducibility vs storage cost)
- Why specific SLAs or schedule times were chosen
- Why certain transformations happen in SQL vs Python
