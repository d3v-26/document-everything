---
name: document-everything
description: Comprehensively documents a codebase by analyzing every file and generating structured markdown documentation. Documents what each file does, why it was written, how components relate, and what architectural decisions were made. Use when the user says "document everything", "document my project", "document this codebase", "what does each file do", "generate docs for my code", "explain my codebase", "why was this coded", "create project documentation", or any variation of wanting to understand or document an existing project.
---

# Document Everything

Generates comprehensive documentation for a codebase: what each file does, why it exists, and how everything fits together.

## Workflow Overview

1. Scan the project with `scan_project.py` → get a file manifest
2. Read the manifest → understand project shape and size
3. Read key files by category (entry → config → source → tests)
4. Generate documentation using templates from `references/doc-templates.md`
5. Write output files
6. Update the project's `CLAUDE.md`

Load `references/file-classification.md` before reading any source files — it explains how to analyze each file type and infer "why" from code signals.

Load `references/doc-templates.md` before writing any output — it provides templates for all output formats.

---

## Step 1: Scan the Project

Run `scan_project.py` from the skill's `scripts/` directory:

```bash
python /path/to/skill/scripts/scan_project.py [project_root]
```

Use the current working directory if the user hasn't specified a path. The script outputs a JSON manifest with all files classified by category.

**If `scan_project.py` can't be located**, fall back to listing files manually: `find . -type f` excluding `node_modules`, `.git`, `__pycache__`, `dist`, `build`.

---

## Step 2: Understand the Project

From the manifest:
- **`size_class`**: determines output format (small → single file, medium/large → directory)
- **`summary.languages`**: determines analysis approach (load relevant sections of file-classification.md)
- **`is_git_repo`**: if true, git history signals are available in the manifest
- **`files` with `category: "entry"`**: read these first — they reveal the overall purpose

If a `README.md` exists, read it first. It often contains the best project description.

Announce to the user: "Scanning complete. Found [N] source files across [languages]. Generating documentation..."

---

## Step 3: Read Files by Priority

Read files in this order, but be smart about quantity:

**Always read:**
- All `entry` files (usually 1-3)
- `README.md` if present
- `package.json`, `pyproject.toml`, or equivalent (reveals dependencies and purpose)
- `Dockerfile` / `docker-compose.yml` if present (reveals deployment context)
- `.env.example` if present (reveals configuration)

**Read representative samples (not exhaustive for large projects):**
- For `source` files: read all if ≤ 20, sample by directory/module if > 20
- For `test` files: read 2-5 to understand testing patterns; note what behavior they protect
- For `config` files: read CI/CD files, build configs

**When sampling large projects:**
- Prioritize files with non-obvious names over obvious ones (`auth_service.py` > `utils.py`)
- Read at least one file from each top-level directory
- Check git commit messages in the manifest to identify recently active files

---

## Step 4: Generate Documentation

### Small project (< 20 source files) → `PROJECT_DOCS.md`

Write a single file at the project root with:
1. Overview section (what + why the project exists)
2. Architecture section (component diagram + relationships)
3. File reference (each source/entry file documented)
4. Architectural decisions (non-obvious choices found in code)

### Medium project (20–100 source files) → `docs/` directory

Create:
- `docs/overview.md` — architecture, entry points, data flows, tech stack
- `docs/files.md` — all source files documented
- `docs/decisions.md` — ADRs for non-obvious choices

### Large project (> 100 source files) → `docs/` with module structure

Create:
- `docs/overview.md` — high-level architecture only
- `docs/modules/[name].md` — one file per top-level directory/package
- `docs/decisions.md` — ADRs

---

## Step 5: Writing Guidelines

**Be specific, not generic.** Bad: "This file handles authentication." Good: "This file implements JWT token validation using the `jose` library, with a 24h expiry and refresh token rotation on each use."

**Document the "why" with evidence.** Bad: "This was written to handle errors." Good: "The retry logic with exponential backoff (lines 45-67) exists because the upstream payment API returns 503s under load — evidenced by the comment `# payment API flaky, see incident-2024-03`."

**Note non-obvious choices.** If a file uses an unusual pattern or library, explain why (if inferable). If a function looks like it could be simpler, note any constraints that required the complexity.

**Extract decisions from code signals:**
- `# HACK:`, `# TODO:`, `# FIXME:` comments → document as known issues
- `legacy`, `compat`, `deprecated` in names → document as transitional code
- Feature flags → document what they enable/disable
- Unusual dependencies → note why they're needed over alternatives

---

## Step 6: Update CLAUDE.md

After generating docs, update (or create) the project's `CLAUDE.md` using the template in `references/doc-templates.md`.

The CLAUDE.md update should include:
- What the project does (1-2 sentences)
- Key files and their roles
- How to run the project
- Where the generated documentation lives

If the project already has a `CLAUDE.md`, add a section at the bottom rather than overwriting existing content.

---

## Communication

- Tell the user what you're doing at each step: "Scanning project...", "Reading entry points...", "Analyzing [N] source files...", "Writing documentation..."
- When done, tell the user exactly what files were created and where
- If the project is large and you sampled files, tell the user which directories you covered and which you skipped
- Offer to go deeper on any specific module if the user wants more detail
