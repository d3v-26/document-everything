# Project Type: Nextflow Pipeline

Guidance for documenting Nextflow bioinformatics workflow pipelines.

## Key Files to Read First

1. `main.nf` or `workflow.nf` — top-level workflow definition
2. `nextflow.config` — profiles, executor settings, resource limits
3. `nextflow_schema.json` — parameter schema (if present)
4. `modules/` — reusable process modules
5. `subworkflows/` — composed sub-pipelines

## Type-Specific Section: Pipeline

Replace the `[Type-Specific Section(s)]` placeholder in the report with:

```markdown
## Pipeline

### Workflow Overview

[Describe the overall biological/data flow — what goes in, what comes out, the high-level stages]

### Processes

| Process | File | Input | Output | Tool/Container |
|---------|------|-------|--------|----------------|
| [PROCESS_NAME] | `[path]` | [input channels] | [output channels] | [tool or container] |

### Channels & Data Flow

[Describe how data moves between processes. Include a diagram if the flow is complex]

```
[input] → PROCESS_A → [channel_1] → PROCESS_B → [output]
                                  ↗
                    [channel_2] ─
```

### Profiles

| Profile | Purpose | Executor |
|---------|---------|---------|
| [name] | [when to use it] | [local/slurm/aws/etc.] |
```

## What to Look For

**In `main.nf` / workflow files:**
- `workflow` block: the top-level orchestration — document the sequence of process calls
- `Channel.fromPath`, `Channel.fromSampleSheet`: reveals input data format
- Process calls with `.collect()`, `.groupTuple()`: reveals fan-in/fan-out patterns

**In `process` blocks:**
- `input:` / `output:` declarations: document exactly what each process consumes and produces
- `script:` block: identify the tool being run (bwa, samtools, gatk, etc.) and key flags
- `container`: reveals the Docker/Singularity image and therefore the tool version
- `label`: maps to resource presets in nextflow.config

**In `nextflow.config`:**
- `profiles`: document each profile and when to use it
- `params`: list all parameters with their defaults and purpose
- `process.memory`, `process.cpus`, `process.time`: document resource requirements per label

**In `modules/`:**
- Each subdirectory is a reusable module — document it like a function (inputs → tool → outputs)
- `meta.yml` files (nf-core style): often contain excellent documentation to quote directly

## Inferring "Why"

- Process names like `ALIGN_READS`, `CALL_VARIANTS` directly state intent
- Container versions reveal specific tool requirements (e.g., `samtools:1.15` — version pinned for reproducibility)
- `// TODO: replace with nf-core module` — signals technical debt
- Multiple profiles (local/cluster/cloud) — reveals the deployment contexts the pipeline supports
- `publishDir` directives — reveal what outputs users are expected to consume
- `errorStrategy 'retry'` — signals known flakiness in a step (document why)

## Common Architectural Decisions to Document

- Why certain processes use specific executors or containers
- Why data is split/merged at specific points (performance vs. memory tradeoffs)
- Why certain tools were chosen over alternatives (bioinformatics often has multiple tools per task)
- Why resource limits are set to specific values
