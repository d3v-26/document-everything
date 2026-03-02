---
name: document-everything
description: Comprehensively documents a codebase by analyzing every file and generating a standardized documentation report. Documents what each file does, why it was written, how components relate, and what architectural decisions were made. Automatically detects project type (Nextflow pipeline, REST API, frontend app, CLI tool, library, data pipeline) and applies the right report template. Use when the user says "document everything", "document my project", "document this codebase", "what does each file do", "generate docs for my code", "explain my codebase", "why was this coded", "create project documentation", "generate a report", or any variation of wanting to understand or document an existing project.
---

# Document Everything

Generates a standardized documentation report for any codebase. Detects the project type, applies the matching template, and produces consistent structured output.

## Workflow Overview

1. Scan the project with `scan_project.py` → JSON manifest with `project_type` and `reading_order`
2. Load `references/doc-templates.md` — the standard report structure
3. Load `references/cross-cutting-standards.md` — Diataxis, MADR ADRs, C4, Keep a Changelog, standard-readme
4. Load the matching type guide from `references/project-types/[type].md`
5. **[Optional]** Check for DeepWiki MCP — if `git_remote` is a public GitHub URL, call DeepWiki MCP to enrich analysis
6. **Pass 1** — Read entry points + README + config → draft outline (sections, component names, key decisions)
7. **Pass 2** — Read remaining files using `reading_order` (priority-sorted) → fill each section with evidence
8. Generate the report using the standard structure + type-specific sections + Mermaid diagrams
9. Write output files
10. Update the project's `CLAUDE.md`

---

## Step 1: Scan the Project

```bash
python /path/to/skill/scripts/scan_project.py [project_root]
```

Use the current working directory if the user hasn't specified a path.

**If `scan_project.py` can't be located**, fall back to: `find . -type f` excluding `node_modules`, `.git`, `__pycache__`, `dist`, `build`.

The manifest now includes:
- `summary.reading_order` — files sorted by priority score (entry points, heavily-imported files, recently-changed files ranked highest). **Use this order when deciding which files to read for large projects.**
- `files[*].priority_score` — numeric score per file
- `files[*].import_count` — how many other files import this file (when > 0)

---

## Step 1b: DeepWiki MCP Enrichment (Optional)

If `summary.git_remote` contains `github.com` and the repo is likely public, check whether the `deepwiki` MCP server is available.

**Setup (one-time, user runs this):**
```bash
claude mcp add -s user -t http deepwiki https://mcp.deepwiki.com/mcp
```

**If available**, call these tools to pre-seed the outline before reading files locally:

| Tool | When to call | What you get |
|------|-------------|-------------|
| `read_wiki_structure` | Always (if MCP available) | Section outline — compare with your own scan |
| `read_wiki_contents` | For medium/large repos | Full wiki content — extract architecture notes, known issues, ADR candidates |
| `ask_question` | When something is unclear from local reads | Targeted answer grounded in the remote codebase |

**How to use the results:** Treat DeepWiki output as a secondary source. Merge its architectural observations into your outline, but always verify against the actual local files. Never copy DeepWiki text verbatim — synthesize it with your own file reads.

**If MCP is not available or repo is private:** skip this step entirely and proceed with local-only analysis.

---

## Step 2: Load Templates and Type Guide

Read `references/doc-templates.md` now — it defines the standard report skeleton used for all output.

Also read `references/cross-cutting-standards.md` now. It defines: Diataxis (how to organize `docs/`), MADR (ADR format), Keep a Changelog, standard-readme structure, and C4 model diagrams. Apply these to every project regardless of type.

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

## Step 3: Two-Pass File Reading

### Pass 1 — Outline (always fast)

Read these files first to draft a structural outline before deep analysis:

1. All `entry` files (usually 1–3)
2. `README.md` if present
3. Primary package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`)
4. `Dockerfile` / `docker-compose.yml` if present
5. `.env.example` if present

After Pass 1: draft section headers, component names, and candidate ADR topics. This outline guides which files to prioritize in Pass 2.

### Pass 2 — Deep Analysis (scale with size_class)

Use `summary.reading_order` from the manifest as your reading queue — it is already sorted by priority (entry → heavily-imported → recently-changed → everything else).

| `size_class` | Read strategy |
|-------------|--------------|
| `small` (< 20 source) | Read all files in `reading_order` |
| `medium` (20–100) | Read all, but skim files > 500 lines (top 100 lines + exports only) |
| `large` (> 100) | Read the top 40 files from `reading_order`; ensure at least 1 file per top-level directory |

**For Nextflow projects, additionally read:**
- `main.nf`, `nextflow.config`, `nextflow_schema.json`
- All files in `modules/` (or the top 20 by priority_score if > 20)

**Tests:** read 2–5 representative test files to understand what behavior is protected.

---

## Step 4: Generate the Report (with Diagrams)

Use the standard report skeleton from `references/doc-templates.md`. Fill in each section:

- **Header block**: project name, type, date, languages, file count, git remote
- **Summary**: 3–5 sentences on purpose, audience, problem solved, approach
- **Architecture**: Mermaid component diagram (`graph TD` or `graph LR`) + table
- **Diagrams**: generate 3–5 Mermaid diagrams inline within relevant sections — see `doc-templates.md` for types (data flow, sequence, dependency graph, ER, state machine). Place each diagram in the section it illustrates, not in a separate "Diagrams" section
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
