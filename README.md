# document-everything

A Claude Code skill that automatically documents any codebase — what each file does, why it was written, how components relate, and what architectural decisions were made.

## Install

In Claude Code, run:

```
/plugin marketplace add d3v-26/document-everything
/plugin install document-everything@d3v-26/document-everything
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
generate docs for my codebase
```

Claude will scan your project, read the files, and produce structured markdown documentation.

## What it generates

| Project size | Output |
|-------------|--------|
| < 20 source files | Single `PROJECT_DOCS.md` at the project root |
| 20–100 source files | `docs/overview.md`, `docs/files.md`, `docs/decisions.md` |
| 100+ source files | `docs/` directory organized by module |

Every run also updates (or creates) the project's `CLAUDE.md` with a summary of key files, tech stack, and how to run the project.

## What gets documented

- **What** — purpose and responsibilities of each file
- **Why** — intent inferred from code comments, naming, git history, and patterns
- **How** — architecture overview showing how components relate
- **Decisions** — non-obvious architectural choices captured as ADRs

## How it works

1. Runs `scripts/scan_project.py` to classify all project files into a JSON manifest
2. Reads entry points, config, and source files (sampling intelligently on large projects)
3. Infers intent from code signals: comments, naming conventions, git commit messages, feature flags
4. Writes documentation adapted to the project's size and structure
5. Updates `CLAUDE.md` with a project summary
