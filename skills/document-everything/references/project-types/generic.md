# Project Type: Generic

Fallback guidance when no specific project type is detected. Use the standard report template from `doc-templates.md` and apply general analysis.

## Type-Specific Section

For generic projects, skip the `[Type-Specific Section(s)]` placeholder or replace it with a **Modules** section based on top-level directory structure:

```markdown
## Modules

| Module | Location | Responsibility |
|--------|---------|----------------|
| [name] | `[path/]` | [what this directory's code does] |
```

## General Analysis Approach

**When project type is unclear:**

1. Start with entry points — they reveal the program's purpose
2. Look at top-level directory names — they usually map to architectural concepts
3. Read `README.md` carefully — it often explains what the project is
4. Check `package.json` description, `pyproject.toml [tool.poetry] description` — often a one-liner summary
5. Look at test file names — they describe behavior in plain language

**Common patterns to identify even without a known type:**

| Pattern | Signals |
|---------|---------|
| `jobs/` or `workers/` | Background job processing |
| `migrations/` | Database with evolving schema |
| `integrations/` or `adapters/` | Bridges to external systems |
| `models/` + `views/` + `controllers/` | MVC architecture |
| `domain/` + `infrastructure/` | Clean / hexagonal architecture |
| `proto/` or `.proto` files | gRPC service |
| `cdk/` or `terraform/` | Infrastructure-as-code |
| `notebooks/` or `.ipynb` | Data science / exploration |

## Still-Useful Sections

Even for unclassified projects, always produce:
- Architecture component diagram (inferred from directory structure)
- Entry points table
- Configuration table (from config files and `.env.example`)
- Dependencies table (from package manifests)
- File reference for all source files
- ADRs for any non-obvious patterns found
