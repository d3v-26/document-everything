# Documentation Report Templates

Standardized Nextflow-inspired report format. All project types use the same structural skeleton — only section content varies. See `project-types/` for type-specific section guidance.

---

## Standard Report Structure

Every report follows this structure, regardless of project type or size:

```markdown
# [Project Name] · Documentation Report

> [One sentence: what this project does]

| | |
|---|---|
| **Type** | [project_type from manifest] |
| **Generated** | [date] |
| **Language(s)** | [languages] |
| **Source files** | [count] |
| **Repository** | [git_remote or —] |

---

## Summary

[3-5 sentences covering: purpose, who uses it, what problem it solves, and the core approach]

---

## Architecture

[Component diagram — ASCII or mermaid. Show top-level components and how data/control flows between them]

**Components:**

| Component | Location | Responsibility |
|-----------|----------|----------------|
| [name] | `[path]` | [what it does] |

---

## Entry Points

| File | Invocation | Purpose |
|------|-----------|---------|
| `[path]` | `[how to run]` | [what it starts] |

---

## [Type-Specific Section(s)]

[See project-types/ reference for what goes here — processes, routes, components, commands, etc.]

---

## Configuration

| Parameter | Location | Purpose | Default |
|-----------|----------|---------|---------|
| [name] | `[file]` | [what it controls] | [value or —] |

---

## Dependencies

| Dependency | Version | Why |
|-----------|---------|-----|
| [name] | [version] | [inferred purpose] |

---

## File Reference

[Per-file entries — see per-file template below]

---

## Architectural Decisions

[ADR entries — see ADR template below]

---

## Known Issues & Technical Debt

| Location | Issue | Severity |
|----------|-------|---------|
| `[file:line]` | [description from TODO/FIXME/HACK comment] | [low/medium/high] |

*Only include if TODO/FIXME/HACK comments are found in the code.*
```

---

## Per-File Entry Template

One entry per source/entry file. Keep to 5–10 lines.

```markdown
### `[relative/path/to/file]`

**Purpose:** [One sentence]

**Why it exists:** [Inferred from code, comments, or git history]

**Key exports:**
- `[Symbol]` — [what it does]

**Notes:** [Gotchas, known issues, non-obvious constraints]
```

Minimal variant for simple/obvious files:

```markdown
### `[path/to/file]`

[One sentence purpose. Key export if non-obvious.]
```

---

## ADR Template

```markdown
### [Short decision title]

**Context:** [Why this decision was needed]

**Decision:** [What was chosen]

**Evidence:** `[file:line]` — [what the code shows]

**Consequence:** [What this enables or constrains]
```

---

## Output Size Rules

| Size class | Source files | Output location |
|-----------|-------------|----------------|
| `small` | < 20 | `PROJECT_DOCS.md` at project root |
| `medium` | 20–100 | `docs/overview.md` + `docs/files.md` + `docs/decisions.md` |
| `large` | > 100 | `docs/overview.md` + `docs/modules/[name].md` + `docs/decisions.md` |

For `large` projects, group files by top-level directory into module files instead of one entry per file.

---

## CLAUDE.md Update Template

```markdown
## [Project Name] — Auto-generated Summary

**What it does:** [1-2 sentences]

**Project type:** [type] | **Stack:** [languages/frameworks]

**Key files:**
| File | Role |
|------|------|
| `[path]` | [purpose] |

**How to run:** `[command from README/Makefile/package.json]`

**Docs generated:** [date] → `[output location]`
```

Add this as a new section at the bottom of an existing CLAUDE.md. Never overwrite existing content.
