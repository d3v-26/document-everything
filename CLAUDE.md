# document-everything

## What This Project Does

A Claude Code skill that documents any codebase using the industry standard for the detected project type. Produces structured, consistent reports covering what each file does, why it was written, architecture, decisions, and configuration.

## Skill Architecture

```
skills/
└── document-everything/
    ├── SKILL.md                                   ← trigger + 8-step workflow
    ├── scripts/
    │   └── scan_project.py                        ← project scanner (JSON manifest + type detection)
    └── references/
        ├── doc-templates.md                       ← standardized Nextflow-inspired report skeleton
        ├── file-classification.md                 ← how to analyze each file type, infer "why"
        ├── cross-cutting-standards.md             ← Diataxis, MADR, Keep a Changelog, C4, standard-readme
        └── project-types/
            ├── nextflow.md                        ← nf-core guidelines
            ├── rest-api.md                        ← OpenAPI 3.1
            ├── frontend.md                        ← Diataxis + Storybook CSF3
            ├── cli.md                             ← POSIX man pages + clig.dev + tldr
            ├── library.md                         ← NumPy / RFC 1574 / JSDoc
            ├── data-pipeline.md                   ← dbt schema.yml + OpenLineage
            └── generic.md                         ← standard-readme + modules table
```

## How the Skill Works

1. Runs `scan_project.py` → JSON manifest with file classification and `project_type`
2. Loads `doc-templates.md` (report skeleton) + `cross-cutting-standards.md`
3. Loads the matching `project-types/[type].md` guide
4. Reads files by priority: entry → README → config → source (sampled for large projects)
5. Generates report using standard structure + type-specific sections
6. Writes output (size-adaptive)
7. Updates project's `CLAUDE.md`

## Project Type Detection

`scan_project.py` detects type from file signatures:

| Type | Key signals |
|------|------------|
| `nextflow` | `.nf` extension, `nextflow.config` |
| `rest-api` | OpenAPI spec, route/controller dirs |
| `frontend` | Vite/Next/Nuxt/Angular config files |
| `cli` | `cli.py`, `commands/` dir, `cmd/` dir |
| `data-pipeline` | `dags/`, `dbt_project.yml`, Prefect/Kedro config |
| `library` | `pyproject.toml`, `Cargo.toml`, `go.mod` + `src/` or `lib/` |
| `generic` | Fallback when no strong signal found |

## Adaptive Output

| Size class | Source files | Output |
|-----------|-------------|--------|
| `small` | < 20 | `PROJECT_DOCS.md` at project root |
| `medium` | 20–100 | `docs/overview.md` + `docs/files.md` + `docs/decisions.md` |
| `large` | > 100 | `docs/overview.md` + `docs/modules/[dir].md` + `docs/decisions.md` |

## Industry Standards Applied

| Standard | Reference | Applied when |
|----------|-----------|-------------|
| nf-core guidelines | nf-co.re/docs/guidelines | `nextflow` projects |
| OpenAPI 3.1 | spec.openapis.org | `rest-api` projects |
| Storybook CSF3 | storybook.js.org | `frontend` projects |
| POSIX man + clig.dev + tldr | clig.dev | `cli` projects |
| NumPy / RFC 1574 / JSDoc | numpydoc.readthedocs.io | `library` projects |
| dbt schema.yml + OpenLineage | docs.getdbt.com | `data-pipeline` projects |
| Diataxis | diataxis.fr | All — docs/ structure |
| MADR ADRs | adr.github.io/madr | All — architectural decisions |
| Keep a Changelog | keepachangelog.com | All — CHANGELOG.md |
| standard-readme | RichardLitt/standard-readme | All — README validation |
| C4 model | c4model.com | All — architecture diagrams |

## Install & Usage

```
/plugin marketplace add d3v-26/document-everything
/plugin install document-everything@document-everything
```

Then just say: `document everything in this project`

## How to Re-package

```bash
cd ~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts
python3 package_skill.py /Users/nik/Desktop/Projects/document-everything/skills/document-everything \
  /Users/nik/Desktop/Projects/document-everything/dist
```

## Key Development Files

| File | Purpose |
|------|---------|
| `DISCOVERY.md` | Initial research on skill system and design decisions |
| `PLAN.md` | Original implementation plan |
| `dist/document-everything.skill` | Packaged skill (zip) ready to install |
| `.claude-plugin/marketplace.json` | Marketplace registration for `/plugin marketplace add` |
