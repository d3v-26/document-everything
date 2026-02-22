# Project Type: Library / Package / SDK

Guidance for documenting reusable libraries and SDKs.

## Key Files to Read First

1. `src/` or `lib/` — the public API surface
2. `__init__.py` / `index.ts` / `mod.rs` — what is exported (the public contract)
3. `pyproject.toml` / `package.json` / `Cargo.toml` — package metadata, version, description
4. Test files — reveal intended usage patterns and edge cases
5. Example files (`examples/`, `demo/`) — show real usage

## Type-Specific Section: Public API

Replace the `[Type-Specific Section(s)]` placeholder in the report with:

```markdown
## Public API

### Exports

| Symbol | Type | File | Purpose |
|--------|------|------|---------|
| `[FunctionName]` | function | `[path]` | [what it does] |
| `[ClassName]` | class | `[path]` | [what it represents] |
| `[TypeName]` | type/interface | `[path]` | [what it describes] |

### Quick Start

```[language]
// Minimal usage example reconstructed from tests/examples
[import statement]

[usage example]
```

### Key Abstractions

[The 2-3 core concepts a user of this library needs to understand]

1. **[Concept]** — [what it is and why it exists]
2. **[Concept]** — [what it is and why it exists]
```

## What to Look For

**In the public entry point (`__init__.py`, `index.ts`):**
- Everything exported here = the intended public API
- Everything NOT exported but in `src/` = internal implementation detail
- Re-exports from sub-modules = intentional surface area

**In class/function definitions:**
- Docstrings and JSDoc comments = intended usage (quote directly if good)
- Parameter types and defaults = the contract
- Return types = what callers receive
- Raised exceptions / error types = failure modes callers must handle

**In tests:**
- Test descriptions are the best documentation of intended behavior
- Edge case tests = known tricky inputs (document these as notes)
- Mock setups = what external dependencies the library expects callers to provide

## Inferring "Why"

- `__all__` in Python = deliberate decision about what is public
- `internal` / `_private` naming = implementation detail not meant for users
- Deprecation decorators/comments = API evolution — what replaced what and why
- Multiple constructor patterns (`from_file`, `from_dict`, `from_url`) = different user contexts
- Abstract base classes / interfaces = extensibility points — document what users can subclass
