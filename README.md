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
- [Contributing](#contributing)

## Install

```
/plugin marketplace add d3v-26/document-everything
/plugin install document-everything@document-everything
```

Restart Claude Code after installing. The skill is auto-detected from context — no slash command needed.

**Already installed?** Run `/plugin update document-everything@document-everything` to pick up the latest version.

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

### DeepWiki MCP (public GitHub repos, free)

For any repo hosted publicly on GitHub, the skill can call Cognition's free DeepWiki MCP to enrich its analysis before reading local files:

```bash
claude mcp add -s user -t http deepwiki https://mcp.deepwiki.com/mcp
```

Once added, the skill automatically uses it when it detects a `github.com` remote. No API key required.

### Local MCP server (any local repo)

`scripts/mcp_server.py` exposes the skill's capabilities as MCP tools so any MCP-compatible client can use them:

| Tool | What it does |
|------|-------------|
| `scan_repo(path)` | Returns the full JSON manifest for a local repo |
| `generate_wiki(path, deep)` | Triggers the full documentation workflow |
| `ask_repo(question, path)` | Answers a specific question about the codebase |

**Setup:**

```bash
pip install mcp

# Claude Code
claude mcp add -s user document-everything python /path/to/skills/document-everything/scripts/mcp_server.py

# Cursor / Windsurf (~/.cursor/mcp.json or mcp_config.json)
{
  "mcpServers": {
    "document-everything": {
      "command": "python",
      "args": ["/path/to/skills/document-everything/scripts/mcp_server.py"]
    }
  }
}
```

---

## Contributing

Bug reports and pull requests welcome at [d3v-26/document-everything](https://github.com/d3v-26/document-everything).

## License

MIT
