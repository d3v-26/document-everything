"""Tests for scan_project() full orchestration."""

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "document-everything" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from scan_project import scan_project


class TestOutputShape:
    def test_top_level_keys(self, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        result = scan_project(str(tmp_plain))
        for key in ("root", "scanned_at", "is_git_repo", "git_remote", "files", "summary"):
            assert key in result

    def test_summary_keys(self, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        result = scan_project(str(tmp_plain))
        for key in ("total_files", "by_category", "languages", "source_file_count",
                     "size_class", "project_type", "reading_order"):
            assert key in result["summary"]

    def test_each_file_has_required_fields(self, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        result = scan_project(str(tmp_plain))
        for f in result["files"]:
            for field in ("path", "name", "size_bytes", "category", "language",
                          "extension", "priority_score"):
                assert field in f, f"Missing '{field}' in file entry: {f}"

    def test_scanned_at_is_iso_datetime(self, tmp_plain):
        (tmp_plain / "x.py").write_text("x")
        result = scan_project(str(tmp_plain))
        dt = datetime.fromisoformat(result["scanned_at"])
        assert dt.tzinfo is not None  # timezone-aware


class TestSizeClasses:
    def _make_source_files(self, root, count, prefix="src"):
        for i in range(count):
            p = root / f"{prefix}{i}.py"
            p.write_text(f"# file {i}")
        return root

    def test_small_less_than_20(self, tmp_plain):
        self._make_source_files(tmp_plain, 5)
        result = scan_project(str(tmp_plain))
        assert result["summary"]["size_class"] == "small"

    def test_medium_at_20(self, tmp_plain):
        self._make_source_files(tmp_plain, 20)
        result = scan_project(str(tmp_plain))
        assert result["summary"]["size_class"] == "medium"

    def test_large_at_100(self, tmp_plain):
        self._make_source_files(tmp_plain, 100)
        result = scan_project(str(tmp_plain))
        assert result["summary"]["size_class"] == "large"

    def test_entry_counts_toward_source_count(self, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        result = scan_project(str(tmp_plain))
        assert result["summary"]["source_file_count"] == 1


class TestExclusionRules:
    def test_node_modules_excluded(self, tmp_plain):
        (tmp_plain / "node_modules").mkdir()
        (tmp_plain / "node_modules" / "dep.js").write_text("x")
        (tmp_plain / "index.js").write_text("x")
        result = scan_project(str(tmp_plain))
        paths = {f["path"] for f in result["files"]}
        assert not any("node_modules" in p for p in paths)

    def test_venv_excluded(self, tmp_plain):
        (tmp_plain / ".venv").mkdir()
        (tmp_plain / ".venv" / "python.py").write_text("x")
        result = scan_project(str(tmp_plain))
        paths = {f["path"] for f in result["files"]}
        assert not any(".venv" in p for p in paths)

    def test_git_dir_excluded(self, tmp_plain):
        (tmp_plain / ".git").mkdir()
        (tmp_plain / ".git" / "HEAD").write_text("ref: refs/heads/main")
        result = scan_project(str(tmp_plain))
        paths = {f["path"] for f in result["files"]}
        assert not any(".git" in p for p in paths)

    def test_hidden_file_excluded(self, tmp_plain):
        (tmp_plain / ".secret").write_text("password")
        result = scan_project(str(tmp_plain))
        paths = {f["path"] for f in result["files"]}
        assert ".secret" not in paths

    def test_gitignore_included_as_config(self, tmp_plain):
        (tmp_plain / ".gitignore").write_text("*.pyc")
        result = scan_project(str(tmp_plain))
        paths = {f["path"] for f in result["files"]}
        assert ".gitignore" in paths

    def test_binary_extensions_excluded(self, tmp_plain):
        (tmp_plain / "image.png").write_bytes(b"\x89PNG\r\n")
        (tmp_plain / "main.py").write_text("x")
        result = scan_project(str(tmp_plain))
        paths = {f["path"] for f in result["files"]}
        assert "image.png" not in paths

    def test_lock_files_excluded(self, tmp_plain):
        (tmp_plain / "package-lock.json").write_text("{}")
        result = scan_project(str(tmp_plain))
        # package-lock.json has .json extension not .lock, but yarn.lock has .lock
        (tmp_plain / "yarn.lock").write_text("x")
        result2 = scan_project(str(tmp_plain))
        paths2 = {f["path"] for f in result2["files"]}
        assert "yarn.lock" not in paths2

    def test_env_example_included(self, tmp_plain):
        (tmp_plain / ".env.example").write_text("KEY=value")
        result = scan_project(str(tmp_plain))
        paths = {f["path"] for f in result["files"]}
        assert ".env.example" in paths


class TestNoneRoot:
    def test_none_uses_cwd(self, monkeypatch, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        monkeypatch.chdir(tmp_plain)
        result = scan_project(None)
        assert result["root"] == str(tmp_plain)


class TestNonGitRepo:
    def test_not_git(self, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        result = scan_project(str(tmp_plain))
        assert result["is_git_repo"] is False
        assert result["git_remote"] is None

    def test_no_git_fields_on_files(self, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        result = scan_project(str(tmp_plain))
        for f in result["files"]:
            assert "last_changed" not in f


class TestGitRepo:
    def test_is_git_true(self, tmp_git_repo):
        (tmp_git_repo / "main.py").write_text("x")
        subprocess.run(["git", "add", "."], cwd=tmp_git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_git_repo, capture_output=True)
        result = scan_project(str(tmp_git_repo))
        assert result["is_git_repo"] is True

    def test_committed_file_has_git_info(self, tmp_git_repo):
        (tmp_git_repo / "main.py").write_text("x")
        subprocess.run(["git", "add", "."], cwd=tmp_git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_git_repo, capture_output=True)
        result = scan_project(str(tmp_git_repo))
        entry = next(f for f in result["files"] if f["path"] == "main.py")
        assert "last_changed" in entry
        assert "last_commit_msg" in entry
