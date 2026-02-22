#!/usr/bin/env python3
"""
scan_project.py — Project structure scanner for document-everything skill

Walks a project directory, classifies files, and outputs a JSON manifest
that Claude uses to understand what to document.

Usage:
    python scan_project.py [project_root]
    python scan_project.py /path/to/project
    python scan_project.py  # uses current directory

Output: JSON to stdout
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

# Directories to always skip
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", ".nuxt", ".output", "out", "coverage",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", "target",
    ".gradle", ".idea", ".vscode", "vendor", "bower_components",
    ".terraform", ".serverless", "tmp", "temp", ".cache", "eggs",
    ".eggs", "*.egg-info"
}

# Binary / generated file extensions to skip content analysis
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".webp",
    ".mp3", ".mp4", ".wav", ".mov", ".avi", ".pdf",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".ttf", ".woff", ".woff2", ".otf", ".eot",
    ".pyc", ".pyo", ".pyd", ".class", ".o", ".so", ".dll", ".dylib",
    ".db", ".sqlite", ".sqlite3",
    ".lock",  # package-lock.json is useful but yarn.lock etc are noise
    ".min.js", ".min.css",
}

# Source code extensions → language mapping
LANGUAGE_MAP = {
    ".py": "python", ".pyw": "python",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".java": "java", ".kt": "kotlin", ".kts": "kotlin",
    ".cs": "csharp",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".c": "c", ".h": "c",
    ".swift": "swift",
    ".php": "php",
    ".r": "r", ".R": "r",
    ".lua": "lua",
    ".scala": "scala",
    ".ex": "elixir", ".exs": "elixir",
    ".hs": "haskell",
    ".clj": "clojure", ".cljs": "clojure",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell", ".fish": "shell",
    ".ps1": "powershell",
    ".sql": "sql",
    ".html": "html", ".htm": "html",
    ".css": "css", ".scss": "scss", ".sass": "sass", ".less": "less",
    ".vue": "vue", ".svelte": "svelte",
    ".dart": "dart",
    ".elm": "elm",
}

# Config file patterns (by name or extension)
CONFIG_NAMES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
    "Pipfile", "Pipfile.lock", "poetry.lock",
    "Cargo.toml", "Cargo.lock",
    "go.mod", "go.sum",
    "Gemfile", "Gemfile.lock",
    "composer.json", "composer.lock",
    "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle",
    "Makefile", "makefile", "GNUmakefile",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    ".env.example", ".env.sample", ".env.template",
    "nginx.conf", "apache.conf",
    "tsconfig.json", "jsconfig.json",
    ".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yaml",
    ".prettierrc", ".prettierrc.js", ".prettierrc.json",
    ".babelrc", "babel.config.js", "babel.config.json",
    "vite.config.js", "vite.config.ts", "webpack.config.js",
    "rollup.config.js", "esbuild.config.js",
    ".gitignore", ".gitattributes",
    "Procfile", "railway.json", "vercel.json", "netlify.toml",
    ".travis.yml", ".circleci", "Jenkinsfile",
    "pyproject.toml", "tox.ini", "pytest.ini", ".flake8", "mypy.ini",
    "CLAUDE.md", "claude.md",
}

CONFIG_EXTENSIONS = {".toml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".config"}

# Entry point patterns
ENTRY_NAMES = {
    "main.py", "app.py", "server.py", "index.py", "run.py", "start.py",
    "main.js", "index.js", "app.js", "server.js",
    "main.ts", "index.ts", "app.ts", "server.ts",
    "main.go", "main.rs", "main.rb", "main.java",
    "index.html", "app.html",
    "__main__.py",
    "Program.cs", "Main.java",
}

# Documentation extensions
DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc", ".org"}
DOC_NAMES = {"README", "CHANGELOG", "CONTRIBUTING", "LICENSE", "AUTHORS",
             "NOTICE", "DISCOVERY", "PLAN", "TODO", "NOTES"}

# Test patterns
TEST_DIR_NAMES = {"test", "tests", "spec", "specs", "__tests__", "e2e", "integration"}
TEST_NAME_PATTERNS = ["test_", "_test.", ".test.", ".spec.", "_spec."]

# Project type detection signatures
# Each entry: (project_type, required_files, optional_boosters)
# required_files: any one of these present → strong signal
# optional_boosters: additional files that raise confidence
PROJECT_TYPE_SIGNATURES: list[tuple[str, set[str], set[str]]] = [
    ("nextflow", {".nf", "nextflow.config", "nextflow_schema.json"}, {"main.nf", "modules/"}),
    ("frontend", {"vite.config.js", "vite.config.ts", "next.config.js", "next.config.ts",
                   "nuxt.config.js", "nuxt.config.ts", "svelte.config.js", "angular.json",
                   "remix.config.js"}, {"index.html", "public/"}),
    ("rest-api", {"openapi.yaml", "openapi.yml", "swagger.yaml", "swagger.yml",
                   "api.py", "routes.py", "router.py", "app.py"}, {"controllers/", "routes/", "handlers/"}),
    ("cli", {"cli.py", "cli.js", "cli.ts", "cmd/", "commands/"}, {"main.py", "main.go"}),
    ("data-pipeline", {"pipeline.py", "dags/", "airflow.cfg", "prefect.yaml",
                        "kedro_pipeline.py", "dbt_project.yml"}, {"data/", "etl/", "transforms/"}),
    ("library", {"setup.py", "pyproject.toml", "Cargo.toml", "go.mod"}, {"src/", "lib/"}),
]


def detect_project_type(files: list[dict], root: Path) -> str:
    """Infer project type from file signatures. Returns type string or 'generic'."""
    all_names = {f["name"] for f in files}
    all_extensions = {f["extension"] for f in files}
    # Top-level directory names
    top_level_dirs = {p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")}

    scores: dict[str, int] = {}

    for project_type, required, boosters in PROJECT_TYPE_SIGNATURES:
        score = 0
        for sig in required:
            if sig.startswith("."):
                # Extension match
                if sig in all_extensions:
                    score += 3
            elif sig.endswith("/"):
                # Directory match
                if sig.rstrip("/") in top_level_dirs:
                    score += 2
            else:
                # Filename match
                if sig in all_names:
                    score += 3
        for sig in boosters:
            if sig.endswith("/"):
                if sig.rstrip("/") in top_level_dirs:
                    score += 1
            elif sig in all_names:
                score += 1
        if score > 0:
            scores[project_type] = score

    if not scores:
        return "generic"

    best = max(scores, key=lambda t: scores[t])

    # Require a minimum signal threshold to avoid false positives
    if scores[best] < 2:
        return "generic"

    # Disambiguate library vs rest-api: if it has route/controller dirs, prefer rest-api
    if best == "library" and any(
        d in top_level_dirs for d in ("routes", "controllers", "handlers", "api")
    ):
        return "rest-api"

    return best


def is_skip_dir(name: str) -> bool:
    return name in SKIP_DIRS or name.startswith(".")


def classify_file(path: Path, rel_path: Path) -> dict:
    """Classify a single file and return its metadata."""
    name = path.name
    suffix = path.suffix.lower()
    parts = rel_path.parts

    # Determine category
    category = "other"
    language = None

    # Check for entry points first (high priority)
    if name in ENTRY_NAMES:
        category = "entry"

    # Docs
    elif suffix in DOC_EXTENSIONS or any(
        name.upper().startswith(n) for n in DOC_NAMES
    ):
        category = "docs"

    # Tests — check directory name or filename pattern
    elif any(p in TEST_DIR_NAMES for p in [p.lower() for p in parts[:-1]]) or \
         any(pat in name.lower() for pat in TEST_NAME_PATTERNS):
        category = "test"

    # Config files
    elif name in CONFIG_NAMES or (
        suffix in CONFIG_EXTENSIONS and name not in {".gitignore"}
    ):
        category = "config"

    # Source code
    elif suffix in LANGUAGE_MAP:
        category = "source"
        language = LANGUAGE_MAP[suffix]

    # Fallback language detection for entry/test
    if language is None and suffix in LANGUAGE_MAP:
        language = LANGUAGE_MAP[suffix]

    stat = path.stat()
    return {
        "path": str(rel_path),
        "name": name,
        "size_bytes": stat.st_size,
        "category": category,
        "language": language,
        "extension": suffix,
    }


def get_git_info(root: Path, rel_path: str) -> dict | None:
    """Get last commit info for a file via git log."""
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "-1", "--format=%ar|%s|%an", "--", rel_path],
            capture_output=True, text=True, cwd=root, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("|", 2)
            return {
                "last_changed": parts[0] if len(parts) > 0 else None,
                "last_commit_msg": parts[1] if len(parts) > 1 else None,
                "last_author": parts[2] if len(parts) > 2 else None,
            }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def is_git_repo(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, text=True, cwd=root, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_git_remote(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, cwd=root, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def scan_project(root_path: str | None = None) -> dict:
    root = Path(root_path or os.getcwd()).resolve()
    git = is_git_repo(root)

    files = []
    by_category: dict[str, int] = {}
    languages: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip dirs in-place
        dirnames[:] = [
            d for d in dirnames
            if not is_skip_dir(d) and d not in SKIP_DIRS
        ]

        for filename in filenames:
            filepath = Path(dirpath) / filename
            suffix = filepath.suffix.lower()

            # Skip binary/generated files
            if suffix in SKIP_EXTENSIONS:
                continue
            # Skip hidden files (but allow .env.example etc)
            if filename.startswith(".") and filename not in CONFIG_NAMES:
                continue

            rel_path = filepath.relative_to(root)
            file_info = classify_file(filepath, rel_path)

            # Add git info for source/entry files (skip for perf on large repos)
            if git and file_info["category"] in ("source", "entry", "config"):
                git_info = get_git_info(root, str(rel_path))
                if git_info:
                    file_info.update(git_info)

            if file_info["language"]:
                languages.add(file_info["language"])

            cat = file_info["category"]
            by_category[cat] = by_category.get(cat, 0) + 1

            files.append(file_info)

    # Sort: entry first, then source, config, test, docs, other
    category_order = {"entry": 0, "source": 1, "config": 2, "test": 3, "docs": 4, "other": 5}
    files.sort(key=lambda f: (category_order.get(f["category"], 99), f["path"]))

    # Project size classification
    source_count = by_category.get("source", 0) + by_category.get("entry", 0)
    if source_count < 20:
        size_class = "small"
    elif source_count < 100:
        size_class = "medium"
    else:
        size_class = "large"

    project_type = detect_project_type(files, root)

    return {
        "root": str(root),
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "is_git_repo": git,
        "git_remote": get_git_remote(root) if git else None,
        "files": files,
        "summary": {
            "total_files": len(files),
            "by_category": by_category,
            "languages": sorted(languages),
            "source_file_count": source_count,
            "size_class": size_class,
            "project_type": project_type,
        },
    }


def main():
    root_path = sys.argv[1] if len(sys.argv) > 1 else None
    manifest = scan_project(root_path)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
