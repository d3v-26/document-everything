# document-everything

## What This Project Does

A Claude Code skill that documents any codebase using the industry standard for the detected project type. Produces structured, consistent reports covering what each file does, why it was written, architecture, decisions, and configuration.

## Skill Architecture

```
skills/
└── document-everything/
    ├── SKILL.md                                   ← trigger + 10-step workflow (two-pass analysis + DeepWiki MCP)
    ├── scripts/
    │   ├── scan_project.py                        ← project scanner (JSON manifest + type detection + priority scoring)
    │   └── mcp_server.py                          ← local MCP server (scan_repo, generate_wiki, ask_repo tools)
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

1. Runs `scan_project.py` → JSON manifest with file classification, `project_type`, and priority-sorted `reading_order`
2. Loads `doc-templates.md` (report skeleton) + `cross-cutting-standards.md`
3. Loads the matching `project-types/[type].md` guide
4. **[Optional]** Calls DeepWiki MCP (`https://mcp.deepwiki.com/mcp`) if repo is public GitHub — enriches outline
5. **Pass 1**: Reads entry points + README + config → drafts structural outline
6. **Pass 2**: Reads files in `reading_order` (priority: entry → heavily-imported → recently-changed) → fills sections
7. Generates report with Mermaid diagrams (architecture, data flow, sequence, ER, state machine)
8. Writes output (size-adaptive)
9. Updates project's `CLAUDE.md`

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

## Running Tests

```bash
make test        # full suite (~80 cases)
make test-fast   # skip integration tests
make test-cov    # with coverage report
```

Tests in `tests/` cover: `classify_file`, `detect_project_type`, priority scoring, import resolution (Python + JS), git helpers, MCP tools, and end-to-end integration against this repo and the fixture projects.

## Key Development Files

| File | Purpose |
|------|---------|
| `DISCOVERY.md` | Initial research on skill system and design decisions |
| `PLAN.md` | Original implementation plan |
| `tests/` | Pytest suite — unit + integration tests for `scan_project.py` and `mcp_server.py` |
| `Makefile` | `make test` / `test-fast` / `test-cov` |
| `dist/document-everything.skill` | Packaged skill (zip) ready to install |
| `.claude-plugin/marketplace.json` | Marketplace registration for `/plugin marketplace add` |
| `.claude-plugin/plugin.json` | Plugin manifest — required for Claude Code to load skills at runtime |

## Plugin System: Two Separate Files

- **`marketplace.json`** — Used only during `/plugin marketplace add` and `/plugin install`. Tells the marketplace system what plugins exist and where skills are.
- **`plugin.json`** — Used at Claude Code startup to load the installed plugin. Without this file, installed skills are never surfaced. Skills auto-discovered from `skills/*/SKILL.md`.

---

## document-everything — Auto-generated Summary

**What it does:** A Claude Code skill that scans any codebase, detects its project type, and generates a structured documentation report with Mermaid diagrams, applying the matching industry standard (nf-core, OpenAPI 3.1, Diataxis, POSIX man pages, NumPy docstrings, dbt schema.yml, or standard-readme). Optionally enriches output via DeepWiki MCP for public GitHub repos.

**Project type:** generic (skill project) | **Stack:** Python (stdlib + `mcp` package for MCP server)

**Key files:**
| File | Role |
|------|------|
| `skills/document-everything/SKILL.md` | Skill entry point — triggers on doc requests, defines 10-step workflow with two-pass analysis |
| `skills/document-everything/scripts/scan_project.py` | Project scanner — classifies files, detects type, computes priority scores + reading_order |
| `skills/document-everything/scripts/mcp_server.py` | Local MCP server — exposes scan_repo, generate_wiki, ask_repo tools |
| `skills/document-everything/references/doc-templates.md` | Standard report skeleton with Mermaid diagram guidance |
| `skills/document-everything/references/cross-cutting-standards.md` | Diataxis, MADR, Keep a Changelog, standard-readme, C4 |
| `skills/document-everything/references/project-types/` | Seven type-specific documentation guides |
| `.claude-plugin/marketplace.json` | Marketplace registration for `/plugin marketplace add d3v-26/document-everything` |

**How to run:** `python skills/document-everything/scripts/scan_project.py [project_root]` (scanner only); full skill via Claude Code natural language prompt.

**Docs generated:** 2026-03-02 → `PROJECT_DOCS.md`
