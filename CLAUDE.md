# document-everything

## Project Goal

Build a Claude Code skill that documents any codebase — what each file does, why it was written, and how everything fits together.

## Current Status

- [x] DISCOVERY.md — research on skill system, design decisions
- [x] PLAN.md — full implementation plan
- [x] Skill scaffold initialized
- [x] `scripts/scan_project.py` written and tested
- [x] `references/file-classification.md` written
- [x] `references/doc-templates.md` written
- [x] `SKILL.md` written
- [x] Packaged as `dist/document-everything.skill`

## Key Files

| File | Purpose |
|------|---------|
| `DISCOVERY.md` | Research findings on skill format, design decisions |
| `PLAN.md` | Step-by-step implementation plan |
| `skills/document-everything/SKILL.md` | Skill trigger + 6-step workflow |
| `skills/document-everything/scripts/scan_project.py` | Walks project dir, classifies files, outputs JSON manifest |
| `skills/document-everything/references/file-classification.md` | How to analyze each file type and infer "why" |
| `skills/document-everything/references/doc-templates.md` | Output templates (overview, per-file, ADR, CLAUDE.md) |
| `dist/document-everything.skill` | Packaged skill ready to install |

## Skill Architecture

```
skills/
└── document-everything/
    ├── SKILL.md                          ← trigger + workflow
    ├── scripts/
    │   └── scan_project.py               ← project scanner (outputs JSON)
    └── references/
        ├── file-classification.md        ← how to analyze file types
        └── doc-templates.md              ← output format templates
```

## Skill Trigger

Triggers when users say things like:
- "document everything", "document my project"
- "what does each file do", "generate docs"
- "explain my codebase", "why was this coded"

## How the Skill Works

1. Runs `scan_project.py` → JSON manifest of all project files
2. Reads manifest to understand size/shape (small/medium/large)
3. Reads files by priority: entry → README → config → source (sampled)
4. Generates adaptive docs: single `PROJECT_DOCS.md` or `docs/` directory
5. Updates project's `CLAUDE.md`

## Adaptive Output

| Project Size | Source Files | Output |
|-------------|-------------|--------|
| Small | < 20 | Single `PROJECT_DOCS.md` |
| Medium | 20–100 | `docs/overview.md` + `docs/files.md` + `docs/decisions.md` |
| Large | > 100 | `docs/overview.md` + `docs/modules/` + `docs/decisions.md` |

## How to Install

```bash
# Install via Claude Code skill installer
# Or drag dist/document-everything.skill into Claude Code
```

## How to Re-package

```bash
cd ~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts
python3 package_skill.py /Users/nik/Desktop/Projects/document-everything/skills/document-everything \
  /Users/nik/Desktop/Projects/document-everything/dist
```
