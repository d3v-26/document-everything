# Project Type: Nextflow Pipeline

Standard: **nf-core guidelines** — the de facto community specification enforced by `nf-core lint`.

Reference: https://nf-co.re/docs/guidelines/pipelines/overview

---

## Required Documentation Files (nf-core standard)

| File | Purpose |
|------|---------|
| `README.md` | Intro, badges, quick-start command |
| `CHANGELOG.md` | Version history (Keep a Changelog format) |
| `CITATIONS.md` | BibTeX citations for all tools used |
| `docs/usage.md` | Full usage documentation |
| `docs/output.md` | Every output file described |
| `nextflow_schema.json` | JSON Schema defining all parameters |

When generating docs for a Nextflow project, produce these files explicitly.

---

## Type-Specific Section: Pipeline

Replace `[Type-Specific Section(s)]` in the report with:

```markdown
## Pipeline

### Workflow Overview

[What goes in, what comes out, the high-level biological/data stages]

### Processes

| Process | File | Input | Output | Tool / Container |
|---------|------|-------|--------|-----------------|
| `PROCESS_NAME` | `modules/…` | [input channels] | [output channels] | [tool:version] |

### Channels & Data Flow

[How data moves between processes]

```
[input] → PROCESS_A → PROCESS_B → [output]
                    ↘ PROCESS_C ↗
```

### Profiles

| Profile | Purpose | Executor |
|---------|---------|---------|
| `standard` | Local dev | local |
| `test` | CI testing | local |
| `[custom]` | [when to use] | [slurm/aws/gcp] |

### Parameters (from nextflow_schema.json)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | string | — | Path to samplesheet CSV |
| `--outdir` | string | `./results` | Output directory |
```

---

## docs/usage.md — Required Sections

Produce this file following the nf-core usage.md standard:

1. Introduction
2. Samplesheet Input — format, column definitions, full examples
3. Running the Pipeline — the typical `nextflow run` command
4. Core Nextflow Arguments — `-profile`, `-resume`, `-c`
5. Pipeline-specific parameter sections (one per major workflow branch)
6. Reference Genome Options (if applicable)
7. Custom Configuration — resource tuning, institutional configs

## docs/output.md — Required Structure

For each process/tool, one subsection:

```markdown
## FastQC

<FastQC description and why it's run in the pipeline>

**Output files:**
- `fastqc/`
  - `*.html`: FastQC report with quality metrics
  - `*.zip`: Zip archive of FastQC report
```

---

## What to Look For

**In `.nf` workflow/process files:**
- `workflow` block → document the top-level orchestration sequence
- `Channel.fromPath`, `Channel.fromSampleSheet` → reveals input format
- `process` blocks → document each: name, inputs, outputs, script tool + key flags
- `container` directive → records tool version for the output.md
- `label` → maps to resource presets in `nextflow.config`
- `publishDir` → reveals what outputs users are expected to consume
- `errorStrategy 'retry'` → document as a known reliability concern

**In `nextflow.config`:**
- `profiles` → document each with name, executor, use case
- `params` → list all with defaults and purpose (also in `nextflow_schema.json`)
- `process.memory/cpus/time` → document resource requirements per label

**In `modules/` (nf-core style):**
- `meta.yml` files → often excellent documentation to quote directly
- Subdirectory = one reusable module → document as inputs → tool → outputs

## Inferring "Why"

- Container pinned to a specific version → reproducibility / known-good toolchain
- Multiple profiles (local/cluster/cloud) → designed for different compute environments
- `// TODO: replace with nf-core module` → technical debt, not yet standardised
- `errorStrategy 'ignore'` → step is optional or expected to fail on some samples
- `collectFile` / `groupTuple` patterns → fan-in/fan-out design decisions

## CITATIONS.md

Extract all tool names and their containers/versions. Produce a CITATIONS.md with BibTeX entries for each tool. Note: many tools have DOIs (BWA, GATK, STAR, etc.); flag any without a citable reference.
