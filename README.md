# document-everything

A Claude Code skill that automatically documents any codebase — following industry standards for each project type.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Project types](#project-types)
- [What it generates](#what-it-generates)
- [Cross-cutting standards](#cross-cutting-standards)
- [How it works](#how-it-works)
- [MCP integrations](#mcp-integrations)
  - [DeepWiki MCP](#deepwiki-mcp--enrich-analysis-for-public-github-repos)
  - [Local MCP server](#local-mcp-server--use-the-skill-from-any-mcp-client)
- [Contributing](#contributing)

## Install

```
/plugin marketplace add d3v-26/document-everything
/plugin install document-everything@document-everything
```

Restart Claude Code after installing. The skill is auto-detected from context — no slash command needed.

**Already installed?** Run `/plugin update document-everything@document-everything` to pick up the latest version.

## Usage

Just tell Claude what you want — no slash command needed:

```
document everything in this project
```

```
what does each file do and why?
```

```
generate a report for my codebase
```

```
explain my codebase
```

Claude will announce the detected project type and file count, then write the report when done:

```
Detected project type: library. Scanning complete — 34 source files in Python.
Generating report...
Report written to docs/overview.md, docs/files.md, docs/decisions.md
```

**Targeting a subdirectory or a different path?** Just mention it:

```
document everything in the api/ directory
```

```
generate docs for ~/Projects/my-other-repo
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
- **Architecture** — Mermaid component diagram + table
- **Diagrams** — 3–5 Mermaid diagrams inline per section: data flow, sequence, dependency graph, ER, state machine
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

1. Runs `scripts/scan_project.py` → JSON manifest with file categories, project type, and a priority-sorted `reading_order` (ranked by import frequency + git recency)
2. Loads the matching project-type guide and cross-cutting standards
3. **[Optional]** Enriches the outline via DeepWiki MCP if the repo is public on GitHub
4. **Pass 1** — reads entry points + README + config to draft a structural outline
5. **Pass 2** — reads remaining files in priority order (most-imported and recently-changed files first)
6. Infers "why" from code signals: comments, naming, git history, feature flags, patterns
7. Generates Mermaid diagrams (architecture, data flow, sequence, ER, state machine) inline in each section
8. Writes the report using the industry-standard structure for the detected type
9. Updates `CLAUDE.md` with a project summary

## MCP integrations

There are two separate MCP integrations — one that *enriches* the skill (DeepWiki), and one that *exposes* the skill to other clients (local server).

### DeepWiki MCP — enrich analysis for public GitHub repos

For repos hosted publicly on GitHub, the skill can call Cognition's free [DeepWiki MCP](https://deepwiki.com) to pre-seed its analysis with remotely-generated wiki content before reading local files. This is purely additive — the skill always performs its own local scan regardless.

**Setup (one-time):**

```bash
claude mcp add -s user -t http deepwiki https://mcp.deepwiki.com/mcp
```

No API key required. Once registered, the skill automatically detects a `github.com` remote and calls DeepWiki before Pass 1. If the MCP is unavailable or the repo is private, this step is silently skipped.

**What it adds:** DeepWiki provides an existing architectural outline and known-issue notes. The skill merges these with its own file reads — never copying verbatim, always verifying against local source.

---

### Local MCP server — use the skill from any MCP client

`scripts/mcp_server.py` exposes the skill's scanner and documentation workflow as three MCP tools, so Cursor, Windsurf, or any other MCP-compatible client can call them directly — without Claude Code installed.

#### Setup

```bash
pip install mcp
```

**Claude Code** (registers for your user, available in all projects):

```bash
claude mcp add -s user document-everything python /path/to/scripts/mcp_server.py
```

**Cursor** (`~/.cursor/mcp.json`) or **Windsurf** (`~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "document-everything": {
      "command": "python",
      "args": ["/path/to/scripts/mcp_server.py"]
    }
  }
}
```

The server runs over **stdio** by default (standard for Claude Code and most clients). To run it as an HTTP server for testing or integration:

```bash
python scripts/mcp_server.py --http        # listens on http://localhost:3333
PORT=8080 python scripts/mcp_server.py --http   # custom port
```

#### Tools

**`scan_repo(path)`**

Scans a local repository and returns the full JSON manifest: file tree with categories, detected project type, size class, per-file priority scores, import counts, and a `reading_order` list sorted by relevance.

```
path  — absolute or relative path to the project root (default: current directory)
```

Returns a JSON string. Useful for building your own tooling on top of the scanner without triggering the full documentation workflow.

---

**`generate_wiki(path, deep)`**

Triggers the complete document-everything workflow for a local repo. Returns a structured prompt with the embedded manifest that Claude executes to produce the report.

```
path  — path to the project root (default: current directory)
deep  — if true, enables deep mode: reads up to 60 files (vs 40), generates 5+ Mermaid diagrams
```

Example — document a repo in deep mode:

```
generate_wiki("/home/user/my-api", deep=True)
```

Output is written to the same adaptive locations as the skill (`PROJECT_DOCS.md`, `docs/`, or `docs/modules/`) depending on project size.

---

**`ask_repo(question, path)`**

Answers a specific question about a codebase without generating a full report. Scans the repo, ranks files by keyword relevance + priority score, and returns a context block (top 15 files + the question) for Claude to answer with file and line-number citations.

```
question  — the question to answer about the codebase (required)
path      — path to the project root (default: current directory)
```

Example:

```
ask_repo("how does authentication work?", "/home/user/my-api")
ask_repo("what does the retry logic do?")   # uses current directory
```

If the answer involves component interactions, Claude will also generate a Mermaid diagram explaining them.

---

## Development

```bash
make test        # run full test suite
make test-fast   # skip integration tests
make test-cov    # with coverage report
```

Tests live in `tests/` and cover the scanner, classifier, project-type detection, import resolution, git helpers, priority scoring, and MCP tools (~80 cases).

## Contributing

Bug reports and pull requests welcome at [d3v-26/document-everything](https://github.com/d3v-26/document-everything).

## License

MIT
