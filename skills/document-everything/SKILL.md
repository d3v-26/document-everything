---
name: document-everything
description: Comprehensively documents a codebase by analyzing every file and generating a standardized documentation report. Documents what each file does, why it was written, how components relate, and what architectural decisions were made. Automatically detects project type (Nextflow pipeline, REST API, frontend app, CLI tool, library, data pipeline) and applies the right report template. Use when the user says "document everything", "document my project", "document this codebase", "what does each file do", "generate docs for my code", "explain my codebase", "why was this coded", "create project documentation", "generate a report", or any variation of wanting to understand or document an existing project.
---

# Document Everything

Generates a standardized documentation report for any codebase. Detects the project type, applies the matching template, and produces consistent structured output.

## Workflow Overview

1. Scan the project with `scan_project.py` → JSON manifest with `project_type`
2. Load `references/doc-templates.md` — the standard report structure used for all output
3. Load the matching type guide from `references/project-types/[type].md`
4. Read files by priority (entry → config → source → tests)
5. Generate the report using the standard structure + type-specific sections
6. Write output files
7. Update the project's `CLAUDE.md`

---

## Step 1: Scan the Project

```bash
python /path/to/skill/scripts/scan_project.py [project_root]
```

Use the current working directory if the user hasn't specified a path.

**If `scan_project.py` can't be located**, fall back to: `find . -type f` excluding `node_modules`, `.git`, `__pycache__`, `dist`, `build`.

---

## Step 2: Load Templates and Type Guide

Read `references/doc-templates.md` now — it defines the standard report skeleton used for all output.

Then read the project-type guide based on `summary.project_type` from the manifest:

| `project_type` | Load |
|---------------|------|
| `nextflow` | `references/project-types/nextflow.md` |
| `rest-api` | `references/project-types/rest-api.md` |
| `frontend` | `references/project-types/frontend.md` |
| `cli` | `references/project-types/cli.md` |
| `library` | `references/project-types/library.md` |
| `data-pipeline` | `references/project-types/data-pipeline.md` |
| `generic` | `references/project-types/generic.md` |

Also load `references/file-classification.md` — it explains how to analyze each file type and infer "why" from code signals.

Announce to the user: "Detected project type: **[type]**. Scanning complete — [N] source files in [languages]. Generating report..."

---

## Step 3: Read Files by Priority

**Always read:**
- All `entry` files (usually 1–3)
- `README.md` if present
- Primary package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`)
- `Dockerfile` / `docker-compose.yml` if present
- `.env.example` if present

**For Nextflow projects, additionally read:**
- `main.nf`, `nextflow.config`, `nextflow_schema.json`
- All files in `modules/` (or a sample if > 20)

**Source file sampling by size:**
- ≤ 20 source files: read all
- 21–100: read all, but skim very large files (> 500 lines) — focus on the top 100 lines + exports
- > 100: read at least one file per top-level directory; prioritize non-obvious filenames

**Tests:** read 2–5 to understand testing patterns. Note what behavior they protect.

---

## Step 4: Generate the Report

Use the standard report skeleton from `references/doc-templates.md`. Fill in each section:

- **Header block**: project name, type, date, languages, file count, git remote
- **Summary**: 3–5 sentences on purpose, audience, problem solved, approach
- **Architecture**: component diagram + table
- **Entry Points**: table of how to invoke the project
- **Type-specific section**: from the project-type guide (processes, routes, commands, etc.)
- **Configuration**: table of all parameters from config files + `.env.example`
- **Dependencies**: table from package manifest with inferred purpose
- **File Reference**: per-file entries for all source/entry files
- **Architectural Decisions**: ADRs for non-obvious choices
- **Known Issues**: any `TODO` / `FIXME` / `HACK` comments found, in a table

Drop any section that genuinely has no content (e.g., no known issues found → omit that section).

### Output location by size

| `size_class` | Write to |
|-------------|---------|
| `small` | `PROJECT_DOCS.md` at project root |
| `medium` | `docs/overview.md` + `docs/files.md` + `docs/decisions.md` |
| `large` | `docs/overview.md` + `docs/modules/[dir].md` per top-level dir + `docs/decisions.md` |

---

## Step 5: Writing Guidelines

**Be specific, not generic.**
- Bad: "This file handles authentication."
- Good: "Implements JWT validation using `jose`, with 24h expiry and refresh token rotation on each use."

**Document the "why" with evidence.**
- Bad: "This was written to handle errors."
- Good: "Retry logic with exponential backoff exists because the upstream payment API returns 503s under load — see comment `# payment API flaky, see incident-2024-03`."

**Every table cell should say something.** If you can't determine the "Why" for a dependency, write "not immediately clear — [what the package name suggests]" rather than leaving it blank.

---

## Step 6: Update CLAUDE.md

After writing the report, append the CLAUDE.md update block from `references/doc-templates.md` to the project's `CLAUDE.md`. Never overwrite existing content — add a new section at the bottom.

---

## Communication

- Announce detected project type and file count before starting analysis
- Name the output file(s) when done: "Report written to `PROJECT_DOCS.md`"
- If large project was sampled, say which directories were covered vs skipped
- Offer to go deeper on any specific module or section
