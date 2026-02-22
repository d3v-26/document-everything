# Discovery: document-everything Skill

## Goal

Build a Claude Code skill that a user can invoke to comprehensively document a codebase — what each file does, why code was written, architectural decisions, and intent behind implementations.

---

## How Claude Code Skills Work

### Structure

A skill is a directory with a required `SKILL.md` and optional bundled resources:

```
skill-name/
├── SKILL.md              ← required; triggers + instructions
├── scripts/              ← executable code (Python/Bash)
├── references/           ← docs loaded into context as needed
└── assets/               ← templates, icons, files used in output
```

### Triggering

- Skills are triggered by matching their `description` field in YAML frontmatter
- **Only** the `name` and `description` frontmatter fields are read initially (before the skill triggers)
- The full SKILL.md body is loaded only after triggering — "progressive disclosure"

### Packaging

- Skills are packaged as `.skill` files (zip archives)
- Use `init_skill.py <name> --path <dir>` to scaffold
- Use `package_skill.py <skill-dir>` to package and validate

### Key Design Principles

1. **Concise is key** — context window is shared with everything else
2. **Progressive disclosure** — metadata → body → references/scripts
3. **Claude is already smart** — only add non-obvious procedural knowledge
4. **Match freedom to task fragility** — specific scripts for deterministic ops, text for flexible ones

---

## What the Skill Needs to Do

### User Experience

User invokes with a natural prompt like:
- "document everything in this project"
- "generate docs for my codebase"
- "what does each file do and why?"

### Core Capabilities

1. **Project analysis** — scan directory structure, identify file types, languages, frameworks
2. **File-level documentation** — for each meaningful file: purpose, responsibilities, key exports/functions
3. **Why documentation** — infer intent from code patterns, comments, git history, naming
4. **Architecture overview** — how files/modules relate to each other
5. **Decision records** — document non-obvious architectural choices
6. **Output** — structured markdown docs in a `docs/` folder or single comprehensive file

### Workflow

```
1. Scan project structure
2. Identify entry points, config files, source files, tests
3. For each file category: read + summarize
4. Generate architecture overview
5. Produce documentation output
6. Update CLAUDE.md with key findings
```

### Output Formats

- `docs/overview.md` — architecture + entry points
- `docs/files/` — per-file documentation
- `docs/decisions.md` — architectural decisions and why
- Or a single `PROJECT_DOCS.md` if the project is small

---

## Key Findings from Existing Skills

### From `doc-coauthoring`
- Multi-stage workflows work well (Context → Drafting → Review)
- Sub-agents can be used for reader testing
- Iterative refinement model is effective

### From `skill-creator`
- Scripts are best for deterministic, reusable operations
- References files are for domain knowledge to load on demand
- Keep SKILL.md under 500 lines; offload detail to references

### From Official Plugin Structure
- Skills can live in `~/.claude/plugins/marketplaces/` or in project-local locations
- `plugin-dev` pattern: organize by capability area

---

## Technical Approach

### What to Script (deterministic, repeated)
- `scan_project.py` — walk directory, classify files, output JSON manifest
- Could use `find`, `git ls-files`, or `os.walk`

### What to Describe in SKILL.md (flexible, context-dependent)
- How to analyze each file type
- How to infer "why" from code evidence
- How to structure docs for different project sizes

### References to Include
- `file-classification.md` — how to categorize different file types
- `doc-templates.md` — templates for different doc sections

---

## Open Questions Resolved

- **Format**: Skill (not a plugin command) — skills are more flexible and context-aware
- **Output**: Adaptive — single file for small projects, structured `docs/` for large ones
- **Git history**: Use `git log --follow` to find context on why files changed
- **CLAUDE.md update**: The skill should always update or create CLAUDE.md with findings
