# Project Type: CLI Tool

Guidance for documenting command-line interface tools.

## Key Files to Read First

1. Entry point (`main.py`, `cli.py`, `main.go`, `bin/` directory)
2. Command definition files (`commands/`)
3. `--help` output if runnable: `python main.py --help`
4. `pyproject.toml` / `package.json` — reveals installed command names and scripts

## Type-Specific Section: Commands

Replace the `[Type-Specific Section(s)]` placeholder in the report with:

```markdown
## Commands

| Command | Subcommand | Arguments | Flags | Purpose |
|---------|-----------|-----------|-------|---------|
| `[tool]` | `[cmd]` | `[args]` | `[--flags]` | [what it does] |

### Usage Examples

```bash
# [What this accomplishes]
[tool] [command] [example args]

# [What this accomplishes]
[tool] [command] --flag [example]
```

### Input / Output

| Command | Reads | Writes | Side Effects |
|---------|-------|--------|-------------|
| [cmd] | [files/stdin/API] | [files/stdout/API] | [what changes in the world] |
```

## What to Look For

**In command definition files:**
- Argument parser setup (`argparse`, `click`, `cobra`, `clap`) = full CLI contract
- `help=` strings = often excellent documentation to quote directly
- `required=True` args = what the user must always provide
- Default values = what the tool assumes without explicit input

**In command handler functions:**
- What files are read/written
- What external services are called
- What output is printed and in what format (text, JSON, table)
- Exit codes used

**In entry point:**
- How commands are registered and dispatched
- Global flags that apply to all commands

## Inferring "Why"

- Multiple output format flags (`--json`, `--csv`, `--table`) = integration with other tools in a pipeline
- `--dry-run` flag = destructive operation, safety conscious design
- `--verbose` / `--quiet` = designed for both interactive and scripted use
- Config file support = complex enough that users need to persist settings
- `--no-color` flag = designed to run in CI environments
