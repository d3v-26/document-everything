# File Classification Guide

Reference for how to analyze and document different file categories found in the project manifest.

---

## Categories

### `entry` — Entry Points

Files where execution begins. These are the most important files to understand first.

**What to document:**
- What the program does when run
- Key command-line args or env vars consumed
- What it initializes (servers, databases, queues)
- How it ties together other modules

**Examples:** `main.py`, `index.js`, `app.ts`, `server.go`, `__main__.py`

---

### `source` — Implementation Files

The core application logic. Document by language:

**Python (`.py`)**
- Summarize: module-level docstring if present, then key classes/functions
- Note decorators that reveal purpose (`@route`, `@celery.task`, `@property`)
- Check for `if __name__ == "__main__"` blocks — reveals dual-use files
- Infer "why": function names, class names, inline comments, type hints

**JavaScript/TypeScript (`.js`, `.ts`, `.jsx`, `.tsx`)**
- Note: `export default` reveals primary export; named exports reveal utilities
- React components: what UI element they render and key props
- API routes: path, method, what data flows in/out
- Hooks: what state or side effect they manage

**Go (`.go`)**
- Package name reveals its role in the module
- Interface definitions reveal contracts between packages
- `func init()` and `func main()` are entry/setup points

**Rust (`.rs`)**
- `pub` vs private items reveal the module's public API
- Traits reveal what behavior is being abstracted
- `mod` declarations show module hierarchy

**Shell scripts (`.sh`, `.bash`)**
- Document: what the script automates, when to run it, required env vars

**SQL (`.sql`)**
- Document: what data the query/schema manages, what business entity it represents

---

### `config` — Configuration Files

Reveal how the project is built, deployed, and configured.

**What to document:**

`package.json` / `pyproject.toml` / `Cargo.toml`:
- Project name and description
- Key dependencies and why they're there (infer from name)
- Scripts/commands defined

`Dockerfile` / `docker-compose.yml`:
- What services are defined
- Exposed ports → reveals what the app serves
- Volumes → reveals persistent data

`Makefile`:
- Available commands and what they do

`.env.example`:
- What env vars are required
- What they configure (API keys, database URLs, feature flags)

CI/CD files (`.github/workflows/*.yml`, `.travis.yml`):
- What environments are tested
- Deployment targets

---

### `test` — Test Files

Document to reveal *what behavior is being protected*.

**What to document:**
- What component/function is being tested
- What scenarios are covered (happy path, edge cases, error cases)
- What the tests reveal about expected behavior (tests are a form of documentation)

---

### `docs` — Documentation Files

**README.md**: Read carefully — it often contains the best high-level description of what the project does.

**CHANGELOG**: Reveals the history of decisions and what changed over time.

**Other .md files**: May contain ADRs (Architecture Decision Records), API docs, guides.

---

## Inferring "Why" — Evidence Sources

When documenting *why* code was written, look for these signals:

### From Code
- **Comments**: `# TODO`, `# FIXME`, `# HACK`, `# NOTE`, `# WHY:` — explicitly flag uncertainty or special cases
- **Function/variable names**: `retryWithBackoff`, `sanitizeUserInput`, `legacyCompatMode` — names reveal intent
- **Error messages**: String literals in exceptions often explain what went wrong and why it matters
- **Feature flags**: Variables named `ENABLE_X`, `USE_NEW_PIPELINE` reveal transitional decisions

### From Git History
- `last_commit_msg` in the manifest reveals recent changes
- Look for messages like "fix: handle edge case where...", "feat: add X to support Y"
- Refactoring commits reveal dissatisfaction with previous approach

### From Surrounding Files
- A file named `compat.py` or `legacy.py` signals backwards compatibility concerns
- Files in `migrations/` reveal schema evolution decisions
- Files in `adapters/` or `wrappers/` reveal integration with external systems

### From Tests
- Test descriptions often explain the "why" ("should handle expired tokens", "should retry on 503")
- Regression tests (often with issue/ticket refs) reveal bugs that were fixed

---

## Architectural Patterns to Identify

Look for these patterns when generating the architecture overview:

| Pattern | Signals |
|---------|---------|
| MVC | `models/`, `views/`, `controllers/` or similar dirs |
| Clean Architecture | `domain/`, `usecases/`, `infrastructure/`, `adapters/` |
| Microservices | Multiple `Dockerfile`s, service-specific dirs, API gateway config |
| Monorepo | `packages/`, `apps/`, `libs/` at root; workspace config in package.json |
| Event-driven | Queue clients, message broker config, event handler files |
| REST API | Route files, controller/handler pattern, OpenAPI/Swagger spec |
| GraphQL | Schema files, resolver files, `schema.graphql` |
| CLI tool | Argument parsing in entry, `commands/` directory |
| Library/SDK | `src/`, `lib/`, well-defined public API, no server entry |
