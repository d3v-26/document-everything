#!/usr/bin/env python3
"""
mcp_server.py — Local MCP server for document-everything

Exposes scan_project.py capabilities as MCP tools so any MCP-compatible
client (Cursor, Windsurf, other Claude Code sessions) can use them.

Tools:
  scan_repo(path)              → JSON manifest (file tree, types, priority order)
  generate_wiki(path)         → Trigger full document-everything workflow (returns instruction)
  ask_repo(path, question)    → Answer a question using the manifest + file content

Usage:
  python mcp_server.py          # stdio (default, for Claude Code)
  python mcp_server.py --http   # HTTP mode on localhost:3333

Claude Code setup (run once):
  claude mcp add -s user document-everything python /path/to/mcp_server.py

Cursor / Windsurf setup (~/.cursor/mcp.json or ~/.codeium/windsurf/mcp_config.json):
  {
    "mcpServers": {
      "document-everything": {
        "command": "python",
        "args": ["/path/to/mcp_server.py"]
      }
    }
  }
"""

import json
import os
import sys
import textwrap
from pathlib import Path

# Ensure scan_project is importable from the same directory
sys.path.insert(0, str(Path(__file__).parent))
from scan_project import scan_project

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print(
        "ERROR: 'mcp' package not installed.\n"
        "Run: pip install mcp\n"
        "Or: uv add mcp",
        file=sys.stderr,
    )
    sys.exit(1)

mcp = FastMCP(
    "document-everything",
    instructions=(
        "Scans and documents codebases. Use scan_repo to get a structured manifest "
        "of any local project, generate_wiki to produce full documentation, or "
        "ask_repo to answer specific questions about a codebase."
    ),
)


@mcp.tool()
def scan_repo(path: str = "") -> str:
    """
    Scan a local repository and return a structured JSON manifest.

    The manifest includes:
    - File tree with categories (entry, source, config, test, docs)
    - Detected project type (nextflow, rest-api, frontend, cli, library, data-pipeline, generic)
    - Size class (small / medium / large)
    - Priority-sorted reading_order for efficient large-repo analysis
    - Per-file priority_score (based on import frequency + git recency)
    - Git metadata (remote URL, last commit per file)

    Args:
        path: Absolute or relative path to the project root. Defaults to current directory.

    Returns:
        JSON string with the full manifest.
    """
    root = str(Path(path).resolve()) if path else os.getcwd()
    try:
        manifest = scan_project(root)
        return json.dumps(manifest, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "path": root})


@mcp.tool()
def generate_wiki(path: str = "", deep: bool = False) -> str:
    """
    Generate comprehensive documentation for a local repository.

    This tool returns a prompt + manifest for Claude to execute the full
    document-everything workflow. Claude will:
    1. Analyze the manifest (file types, project type, reading order)
    2. Read files in priority order using two-pass analysis
    3. Generate Mermaid diagrams (architecture, data flow, sequence)
    4. Write structured docs to the appropriate output location
    5. Update CLAUDE.md

    Args:
        path: Absolute or relative path to the project root. Defaults to current directory.
        deep: If True, enables multi-pass deep research mode (reads more files, more diagrams).

    Returns:
        A structured prompt with the manifest embedded, ready for Claude to execute.
    """
    root = str(Path(path).resolve()) if path else os.getcwd()
    try:
        manifest = scan_project(root)
    except Exception as e:
        return f"ERROR scanning {root}: {e}"

    summary = manifest["summary"]
    size_class = summary["size_class"]
    project_type = summary["project_type"]
    source_count = summary["source_file_count"]
    languages = ", ".join(summary["languages"]) or "unknown"
    git_remote = manifest.get("git_remote") or "—"
    reading_order = summary.get("reading_order", [])

    top_files = reading_order[:10]
    top_files_str = "\n".join(f"  - {p}" for p in top_files)

    output_location = {
        "small": "`PROJECT_DOCS.md` at project root",
        "medium": "`docs/overview.md` + `docs/files.md` + `docs/decisions.md`",
        "large": "`docs/overview.md` + `docs/modules/[dir].md` + `docs/decisions.md`",
    }.get(size_class, "`PROJECT_DOCS.md`")

    deep_note = (
        "\n**DEEP MODE**: Use multi-pass analysis. Pass 1: outline from entry+README+config. "
        "Pass 2: read top 60 files from reading_order, filling each section with evidence. "
        "Generate 5+ Mermaid diagrams."
        if deep else
        "\nGenerate 3–5 Mermaid diagrams (architecture, data flow, sequence)."
    )

    return textwrap.dedent(f"""
        ## document-everything: Generate Wiki

        **Project:** `{root}`
        **Type:** {project_type} | **Size:** {size_class} ({source_count} source files)
        **Languages:** {languages}
        **Git remote:** {git_remote}
        **Output:** {output_location}
        {deep_note}

        ### Manifest (JSON)
        ```json
        {json.dumps(manifest, indent=2)}
        ```

        ### Instructions
        Execute the document-everything workflow:
        1. Use the manifest above (skip re-scanning)
        2. Load `references/doc-templates.md` and the `{project_type}` type guide
        3. Read files in this priority order (top 10 shown):
        {top_files_str}
        4. Generate the report with Mermaid diagrams in each section
        5. Write to {output_location}
        6. Update `CLAUDE.md`
    """).strip()


@mcp.tool()
def ask_repo(question: str, path: str = "") -> str:
    """
    Answer a specific question about a local repository.

    Scans the repo, selects the most relevant files based on the question,
    and returns a structured context block for Claude to answer with.

    Args:
        question: The question to answer about the codebase.
        path: Absolute or relative path to the project root. Defaults to current directory.

    Returns:
        A context block with manifest + relevant file list + the question, ready for Claude.
    """
    root = str(Path(path).resolve()) if path else os.getcwd()
    try:
        manifest = scan_project(root)
    except Exception as e:
        return f"ERROR scanning {root}: {e}"

    summary = manifest["summary"]
    project_type = summary["project_type"]
    reading_order = summary.get("reading_order", [])

    # Simple keyword-based relevance: score files by how many question words appear in their path
    question_words = set(question.lower().split())
    stopwords = {"the", "a", "an", "is", "in", "of", "to", "for", "how", "what", "why",
                 "does", "do", "are", "this", "that", "it", "and", "or", "with"}
    keywords = question_words - stopwords

    def relevance(p: str) -> int:
        p_lower = p.lower()
        return sum(1 for kw in keywords if kw in p_lower)

    # Blend reading_order priority with keyword relevance
    scored = []
    order_map = {p: i for i, p in enumerate(reading_order)}
    for f in manifest["files"]:
        if f["category"] not in ("entry", "source", "config"):
            continue
        kw_score = relevance(f["path"]) * 10
        order_score = max(0, 50 - order_map.get(f["path"], 50))
        scored.append((kw_score + order_score, f["path"]))

    scored.sort(reverse=True)
    top_relevant = [p for _, p in scored[:15]]
    files_str = "\n".join(f"  - {p}" for p in top_relevant)

    return textwrap.dedent(f"""
        ## ask_repo: Answer a Question

        **Project:** `{root}` ({project_type})
        **Question:** {question}

        ### Relevant files to read (ranked by relevance + priority)
        {files_str}

        ### Instructions
        1. Read the files listed above from `{root}/`
        2. Answer the question: **{question}**
        3. Cite specific files and line numbers where relevant
        4. If the answer requires understanding how components interact, generate a Mermaid diagram
    """).strip()


if __name__ == "__main__":
    if "--http" in sys.argv:
        # HTTP mode — useful for testing with curl
        port = int(os.environ.get("PORT", "3333"))
        print(f"Starting document-everything MCP server on http://localhost:{port}", file=sys.stderr)
        mcp.run(transport="streamable-http", host="localhost", port=port)
    else:
        # Default: stdio (Claude Code standard)
        mcp.run(transport="stdio")
