# Project Type: CLI Tool

Standards: **POSIX man page spec** + **CLI Guidelines (clig.dev)** + **tldr-pages format** — best-in-class CLIs satisfy all three.

References:
- https://clig.dev/
- https://man7.org/linux/man-pages/man7/man-pages.7.html
- https://github.com/tldr-pages/tldr/blob/main/contributing-guides/style-guide.md

---

## Type-Specific Section: Commands

Replace `[Type-Specific Section(s)]` in the report with:

```markdown
## Commands

### Synopsis

```
[tool] [global options] <command> [command options] [arguments]
```

### Command Reference

| Command | Subcommand | Arguments | Flags | Purpose |
|---------|-----------|-----------|-------|---------|
| `[tool]` | `[cmd]` | `<required>` `[optional]` | `--flag` | [what it does] |

### Global Options

| Flag | Short | Default | Purpose |
|------|-------|---------|---------|
| `--verbose` | `-v` | false | Enable verbose output |
| `--config` | `-c` | `~/.config/tool/config.yaml` | Config file path |
| `--output` | `-o` | `stdout` | Output destination |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Misuse of command / invalid arguments |
| [n] | [tool-specific meaning] |

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `[TOOL]_CONFIG` | Path to config file | `~/.config/tool/` |
| `[TOOL]_LOG_LEVEL` | Log verbosity | `info` |

### Usage Examples

```bash
# [What this accomplishes]
[tool] [command] [example args]

# [What this accomplishes — edge case or advanced use]
[tool] [command] --flag [example] | [tool] [other-command]
```
```

---

## clig.dev `--help` Output Standard

Every CLI tool must satisfy these conventions. Check the project against them:

**Required behaviors:**
- `--help` always works, regardless of other flags or context
- Short (`-h`) emits a concise 1-2 sentence summary + pointer to `--help`
- `--help` output goes to `stdout` (not `stderr`)
- Long-form options (`--verbose`) always exist alongside short forms (`-v`)
- `--version` / `-V` flag always exists
- Machine-parseable output mode (`--json`, `--format json`) if the tool is scripting-facing

**Ideal `--help` format:**
```
Usage: [tool] [OPTIONS] <INPUT>

[One-line description]

Arguments:
  <INPUT>  [description]

Options:
  -o, --output <PATH>  [description] [default: stdout]
  -v, --verbose        [description]
      --format <FMT>   [possible values: json, csv, text]
  -h, --help           Print help
  -V, --version        Print version

Examples:
  [tool] [common invocation]
  [tool] --format json [input] > [output]

Docs: https://[project-url]/docs
```

---

## tldr-page Format

Produce a `docs/tldr.md` or `tldr/[tool].md` in this exact format:

```markdown
# [tool]

> [One-line description of what the tool does.]
> More information: <https://[project-url]>.

- [Common use case description]:

`[tool] {{path/to/file}}`

- [Another common use case]:

`[tool] [command] --flag {{value}}`

- [Edge case or advanced use]:

`[tool] [command] {{input}} | [tool] [other-command]`
```

Rules:
- Description in `>` blockquote (max 2 lines)
- 3–8 examples total
- Placeholders use `{{double_curly_braces}}`
- Prefer `--long-form` flags in examples
- Description lines use imperative mood

---

## POSIX Man Page Sections

For installed system tools, document in this order:

| Section | Content |
|---------|---------|
| `NAME` | `command - one-line description` |
| `SYNOPSIS` | Formal syntax: `command [-flags] [options] argument` |
| `DESCRIPTION` | Full behavior description |
| `OPTIONS` | Each flag, long form first: `--verbose, -v` |
| `EXIT STATUS` | Numeric codes and their meanings |
| `ENVIRONMENT` | Environment variables consumed |
| `FILES` | Config files, state files, cache paths |
| `EXAMPLES` | Common real-world invocations |
| `BUGS` | Known limitations |
| `SEE ALSO` | Related commands |

---

## What to Look For

**In argument parser setup (`argparse`, `click`, `cobra`, `clap`):**
- `help=` strings → often the best documentation; quote them directly
- `required=True` → what the user must always provide
- Default values → what the tool assumes without explicit input
- `choices` / `possible_values` → constrained inputs to document

**In command handler functions:**
- Files read/written → I/O contract
- External services called → dependencies
- Output format printed → what stdout looks like
- Exit code logic → document non-zero codes

## Inferring "Why"

- Multiple output formats (`--json`, `--csv`, `--table`) → designed for scripting pipelines
- `--dry-run` flag → destructive operation; safety-first design decision
- `--no-color` / `NO_COLOR` env var support → designed for CI/non-interactive use
- Config file support → complex enough that users need persistent settings
- `--quiet` + `--verbose` both exist → designed for both interactive and scripted contexts
- Pagination (`--page`, `--limit`) → large dataset awareness
