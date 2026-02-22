# document-everything

A Claude Code skill that automatically documents any codebase — following industry standards for each project type.

## Install

```
/plugin marketplace add d3v-26/document-everything
/plugin install document-everything@document-everything
```

## Usage

Just tell Claude what you want:

```
document everything in this project
```

```
what does each file do and why?
```

```
generate a report for my codebase
```

## Project types

The skill auto-detects your project type and applies the matching industry standard:

| Type | Detected by | Standard applied |
|------|------------|-----------------|
| **Nextflow pipeline** | `.nf` files, `nextflow.config` | nf-core guidelines — generates `docs/usage.md`, `docs/output.md`, `CITATIONS.md` |
| **REST API** | OpenAPI/Swagger specs, route files | OpenAPI 3.1 — endpoints table, auth, schemas, error codes |
| **Frontend app** | Vite/Next/Nuxt/Angular configs | Diataxis framework + Storybook CSF3 |
| **CLI tool** | `cli.py`, `commands/`, argparse | POSIX man pages + clig.dev + tldr-pages format |
| **Library / SDK** | `pyproject.toml`, `Cargo.toml`, `go.mod` | NumPy docstrings (Python), RFC 1574 (Rust), JSDoc (TS/JS) |
| **Data pipeline** | dbt, Airflow, Prefect, Kedro | dbt schema.yml conventions + OpenLineage |
| **Generic** | Fallback | standard-readme + modules table |

## What it generates

**Adaptive output by project size:**

| Source files | Output |
|-------------|--------|
| < 20 | `PROJECT_DOCS.md` at project root |
| 20–100 | `docs/overview.md` · `docs/files.md` · `docs/decisions.md` |
| 100+ | `docs/overview.md` · `docs/modules/[name].md` · `docs/decisions.md` |

**Every report includes:**

- **Header block** — project type, language(s), file count, git remote
- **Summary** — what it does, who uses it, the core approach
- **Architecture** — C4-style component diagram + table
- **Entry points** — how to invoke the project
- **Type-specific section** — processes, routes, commands, exports, models, etc.
- **Configuration** — all parameters from config files and `.env.example`
- **Dependencies** — with inferred purpose for each
- **File reference** — every source file documented
- **Architectural decisions** — MADR-format ADRs for non-obvious choices
- **Known issues** — all `TODO` / `FIXME` / `HACK` comments surfaced in a table

Every run also updates (or creates) the project's `CLAUDE.md`.

## Cross-cutting standards

Regardless of project type, every report applies:

- [**Diataxis framework**](https://diataxis.fr/) — docs organized into Tutorials / How-to / Reference / Explanation
- [**MADR ADRs**](https://adr.github.io/madr/) — architectural decisions in `docs/decisions/`
- [**Keep a Changelog**](https://keepachangelog.com/) — checks for and generates `CHANGELOG.md`
- [**standard-readme**](https://github.com/RichardLitt/standard-readme) — validates README structure
- [**C4 model**](https://c4model.com/) — architecture diagrams in Mermaid

## How it works

1. Runs `scripts/scan_project.py` → classifies every file into a JSON manifest, detects project type
2. Loads the matching project-type guide and cross-cutting standards
3. Reads files by priority: entry points → config → source (sampled intelligently on large projects)
4. Infers "why" from code signals: comments, naming, git history, feature flags, patterns
5. Writes the report using the industry-standard structure for the detected type
6. Updates `CLAUDE.md` with a project summary
