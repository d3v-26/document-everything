# Plan: document-everything Skill

## Overview

Build a Claude Code skill named `document-everything` that intelligently documents any codebase — producing structured, meaningful documentation about what code does, why it exists, and how it's organized.

---

## Skill Structure

```
document-everything/
├── SKILL.md                    ← trigger description + workflow
├── scripts/
│   └── scan_project.py         ← walk dir tree, classify files, output JSON manifest
└── references/
    ├── file-classification.md  ← how to categorize file types (config, source, test, etc.)
    └── doc-templates.md        ← output templates for overview, per-file, decisions
```

No `assets/` needed — output is generated markdown, not template-based.

---

## Implementation Steps

### Step 1: Initialize Skill with `init_skill.py`

```bash
python ~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts/init_skill.py \
  document-everything \
  --path /Users/nik/Desktop/Projects/document-everything
```

This scaffolds the directory structure.

### Step 2: Write `scripts/scan_project.py`

**Purpose:** Walk the project directory and produce a JSON manifest:
```json
{
  "root": "/path/to/project",
  "git_root": true,
  "files": [
    {
      "path": "src/auth.js",
      "size_bytes": 1234,
      "category": "source",
      "language": "javascript",
      "last_modified": "2024-01-15"
    }
  ],
  "summary": {
    "total_files": 42,
    "by_category": { "source": 20, "config": 5, "test": 10, "docs": 2, "other": 5 },
    "languages": ["python", "javascript"]
  }
}
```

**File categories:**
- `source` — actual implementation code (.py, .js, .ts, .go, etc.)
- `config` — package.json, pyproject.toml, .env.example, Makefile, etc.
- `test` — files in test/ or named *.test.*, *_test.*, *spec*
- `docs` — .md, .rst, .txt documentation
- `entry` — main.py, index.js, app.py, server.ts (entry points)
- `other` — everything else

**Key behaviors:**
- Skip: node_modules, .git, __pycache__, .venv, dist, build, .next
- Respect .gitignore if present
- Include git stats per file if in a git repo (`git log --follow -1 --format="%ar|%s"`)

### Step 3: Write `references/file-classification.md`

Reference doc Claude loads to understand how to analyze different file types:
- How to interpret Python vs JS vs Go files
- What to look for in config files
- How to extract "why" signals from code (comments, naming, git messages)
- How to identify architectural patterns (MVC, microservices, monorepo, etc.)

### Step 4: Write `references/doc-templates.md`

Templates for consistent output:
- Project overview template
- Per-file documentation template
- Architecture diagram (ASCII or mermaid)
- Decision record template (ADR format)

### Step 5: Write `SKILL.md`

**Frontmatter description** should trigger on:
- "document everything", "document my project", "document this codebase"
- "what does each file do", "generate docs", "explain my code"
- "why was this coded", "code documentation"

**Workflow in SKILL.md:**
```
1. Run scan_project.py → get manifest
2. Read manifest → understand project size/shape
3. For each file category, read representative files
4. Generate documentation (adaptive to project size)
5. Write output files
6. Update or create CLAUDE.md
```

**Adaptive output strategy:**
- Small project (< 20 source files): single `PROJECT_DOCS.md`
- Medium project (20–100 files): `docs/overview.md` + `docs/files/` directory
- Large project (> 100 files): `docs/` with architecture, modules, decisions

### Step 6: Package the skill

```bash
python ~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts/package_skill.py \
  /Users/nik/Desktop/Projects/document-everything/document-everything \
  /Users/nik/Desktop/Projects/document-everything/dist
```

---

## CLAUDE.md Strategy

CLAUDE.md is created/updated at **each major step**:

| Step | CLAUDE.md Update |
|------|-----------------|
| After DISCOVERY.md | Add project goal and discovery findings |
| After PLAN.md | Add implementation plan summary |
| After skill initialized | Add skill structure info |
| After coding | Add usage instructions + file locations |
| After packaging | Add how to install and use |

---

## Success Criteria

1. Running the skill on any project produces meaningful documentation
2. The "why" section explains non-obvious decisions using evidence from code/git
3. Output adapts to project size (single file vs directory structure)
4. CLAUDE.md is always updated with project context
5. Skill packages cleanly with `package_skill.py`

---

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Large projects with 1000s of files | scan_project.py limits to representative sample; SKILL.md instructs batching |
| Binary/generated files | scan_project.py excludes known generated paths and binary extensions |
| No git history | Gracefully degrade — skip git stats, still document from code |
| Token limits | Progressive disclosure: read files in batches by category |
