# Project Type: Library / Package / SDK

Standards vary by language. Use the language-native standard.

| Language | Docstring Standard | Generator | Reference |
|----------|-------------------|-----------|-----------|
| Python | NumPy or Google style | Sphinx + autodoc | https://numpydoc.readthedocs.io |
| TypeScript/JS | JSDoc | TypeDoc | https://typedoc.org |
| Rust | `///` doc comments (RFC 1574) | rustdoc (`cargo doc`) | https://rust-lang.github.io/api-guidelines/documentation.html |
| Go | godoc conventions | pkgsite | https://pkg.go.dev |
| Java | Javadoc | javadoc | standard JDK |

---

## Type-Specific Section: Public API

Replace `[Type-Specific Section(s)]` in the report with:

```markdown
## Public API

### Exports

| Symbol | Type | File | Purpose |
|--------|------|------|---------|
| `[FunctionName(args) → ReturnType]` | function | `[path]` | [what it does] |
| `[ClassName]` | class | `[path]` | [what it represents] |
| `[TypeName]` | type/interface | `[path]` | [what it describes] |

### Quick Start

```[language]
[import statement]

[Minimal working example reconstructed from tests or examples/]
```

### Key Concepts

[The 2-3 abstractions a user must understand to use this library]

1. **[Concept]** — [what it is and why it exists]
2. **[Concept]** — [what it is and why it exists]

### Error Handling

| Error / Exception | Raised When | How to Handle |
|------------------|-------------|--------------|
| `[ErrorType]` | [condition] | [recommended handling] |
```

---

## NumPy Docstring Sections (Python)

For Python libraries, document each public function/class following NumPy style:

```python
def function(param1, param2):
    """
    Short one-line summary. (Third-person present tense, no variable names.)

    Extended summary: 2-5 sentences explaining when and why to use this.

    Parameters
    ----------
    param1 : type
        Description of param1. Include units if numeric.
    param2 : type, optional
        Description. Default is X.

    Returns
    -------
    result : type
        Description of return value.

    Raises
    ------
    ValueError
        If param1 is negative.

    See Also
    --------
    related_function : Brief description.

    Examples
    --------
    >>> result = function(1, 2)
    >>> result
    3
    """
```

Required sections: short summary, Parameters, Returns.
Strongly recommended: Examples (must be doctest-runnable), Raises, See Also.

---

## Rust Documentation Sections (RFC 1574)

```rust
/// Short one-line summary. (Third-person present tense.)
///
/// Extended description: when and why to use this.
///
/// # Examples
///
/// ```
/// let result = my_function(42);
/// assert_eq!(result, 84);
/// ```
///
/// # Panics
///
/// Panics if `n` is zero.
///
/// # Errors
///
/// Returns `Err(ParseError)` if input is not valid UTF-8.
///
/// # Safety
///
/// (unsafe fn only) Caller must ensure `ptr` is non-null and valid.
```

Per Rust API Guidelines (C-CRATE-DOC), crate-level docs (`lib.rs`) must include:
- What the crate does and why (elevator pitch)
- Short working runnable example
- Links to primary types and entry points

---

## Full Doc Site Structure (Diataxis)

Organize the generated docs directory following the Diataxis framework:

```
docs/
├── tutorials/          ← Learning-oriented: step-by-step guides for new users
│   └── getting-started.md
├── how-to/             ← Task-oriented: recipes for specific goals
│   └── how-to-*.md
├── reference/          ← Information-oriented: API reference (auto-generated)
│   └── api.md
└── explanation/        ← Understanding-oriented: why decisions were made
    └── design.md
```

Keep these four types strictly separate — do not mix tutorial content with reference docs.

---

## What to Look For

**In the public entry point (`__init__.py`, `index.ts`, `lib.rs`):**
- Everything exported = intended public API
- Everything NOT exported but in `src/` = internal detail (note this distinction)
- Re-exports from sub-modules = intentional surface area

**In class/function definitions:**
- Existing docstrings/JSDoc → quote and build on them, don't paraphrase
- Parameter types and defaults → the contract
- Return types → what callers receive
- Raised exceptions / `Result` error types → failures callers must handle

**In tests:**
- Test descriptions are the best documentation of intended behavior
- Edge case tests → known tricky inputs; document as notes
- Mock setups → external dependencies callers must provide

## Inferring "Why"

- `__all__` in Python → deliberate decision about what is public
- `pub(crate)` in Rust → intentionally not public API
- Deprecation decorators → API evolution; document what replaced it and why
- Multiple constructor patterns (`from_file`, `from_dict`, `from_url`) → different user contexts
- Abstract base classes / traits → extensibility points; document what users can implement
- Semver major bump in changelog → breaking change; document what changed
