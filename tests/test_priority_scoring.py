"""Tests for priority_score formula and reading_order in scan_project.py."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "document-everything" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from scan_project import scan_project


class TestCategoryBases:
    def _scan_category(self, tmp_plain, filename, content="x"):
        """Scan a single file and return its priority_score."""
        (tmp_plain / filename).write_text(content)
        manifest = scan_project(str(tmp_plain))
        files = {f["path"]: f for f in manifest["files"]}
        return files.get(filename, {}).get("priority_score")

    def test_entry_base_is_100(self, tmp_plain):
        score = self._scan_category(tmp_plain, "main.py")
        assert score == 100  # non-git → recency=0, no imports → base only

    def test_source_base_is_50(self, tmp_plain):
        score = self._scan_category(tmp_plain, "logic.py")
        assert score == 50

    def test_config_base_is_30(self, tmp_plain):
        score = self._scan_category(tmp_plain, "pyproject.toml")
        assert score == 30

    def test_docs_base_is_20(self, tmp_plain):
        score = self._scan_category(tmp_plain, "README.md")
        assert score == 20

    def test_test_base_is_10(self, tmp_plain):
        score = self._scan_category(tmp_plain, "test_logic.py")
        assert score == 10

    def test_other_base_is_0(self, tmp_plain):
        score = self._scan_category(tmp_plain, "schema.graphql")
        assert score == 0


class TestImportCountField:
    def test_no_import_count_field_when_zero(self, tmp_plain):
        """import_count field only present when > 0."""
        (tmp_plain / "main.py").write_text("print('hello')")
        manifest = scan_project(str(tmp_plain))
        f = next(x for x in manifest["files"] if x["path"] == "main.py")
        assert "import_count" not in f

    def test_import_count_field_when_positive(self, tmp_plain):
        """import_count field set when a file is imported by others."""
        (tmp_plain / "utils.py").write_text("def x(): pass")
        (tmp_plain / "main.py").write_text("from .utils import x")
        manifest = scan_project(str(tmp_plain))
        f = next(x for x in manifest["files"] if x["path"] == "utils.py")
        assert f.get("import_count", 0) >= 1


class TestImportScoring:
    def test_import_adds_5_per_reference(self, tmp_plain):
        """3 files importing utils.py → priority_score += 15."""
        (tmp_plain / "utils.py").write_text("def x(): pass")
        for i in range(3):
            (tmp_plain / f"user{i}.py").write_text("from .utils import x")
        manifest = scan_project(str(tmp_plain))
        f = next(x for x in manifest["files"] if x["path"] == "utils.py")
        # base=50 (source) + 0 (recency, non-git) + 15 (3 imports × 5)
        assert f["priority_score"] == 65
        assert f["import_count"] == 3


class TestRecencyScoring:
    def test_non_git_recency_is_zero(self, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        manifest = scan_project(str(tmp_plain))
        f = next(x for x in manifest["files"] if x["path"] == "main.py")
        # score = 100 (entry) + 0 (non-git recency) + 0 (no imports)
        assert f["priority_score"] == 100

    def test_recency_adds_to_base(self, tmp_plain):
        """Mocked recency=20, imports=20: source file score = 50 + 20 + 20 = 90."""
        (tmp_plain / "utils.py").write_text("def x(): pass")

        fake_recency = {"utils.py": 20}
        fake_imports = {"utils.py": 4}  # 4 × 5 = 20

        with patch("scan_project.get_recently_changed_files", return_value=fake_recency), \
             patch("scan_project.compute_import_references", return_value=fake_imports), \
             patch("scan_project.is_git_repo", return_value=True), \
             patch("scan_project.get_git_info", return_value=None), \
             patch("scan_project.get_git_remote", return_value=None):
            manifest = scan_project(str(tmp_plain))

        f = next(x for x in manifest["files"] if x["path"] == "utils.py")
        assert f["priority_score"] == 90  # 50 + 20 + 20


class TestReadingOrder:
    def test_reading_order_only_entry_source_config(self, tmp_plain):
        """reading_order contains only entry/source/config paths."""
        for name in ("main.py", "logic.py", "README.md", "test_logic.py", "schema.graphql"):
            (tmp_plain / name).write_text("x")
        manifest = scan_project(str(tmp_plain))
        order = manifest["summary"]["reading_order"]
        all_files = {f["path"]: f for f in manifest["files"]}
        for path in order:
            assert all_files[path]["category"] in ("entry", "source", "config")

    def test_reading_order_sorted_descending(self, tmp_plain):
        """reading_order is sorted by priority_score descending."""
        for name in ("main.py", "logic.py", "helper.py"):
            (tmp_plain / name).write_text("x")
        manifest = scan_project(str(tmp_plain))
        order = manifest["summary"]["reading_order"]
        all_files = {f["path"]: f for f in manifest["files"]}
        scores = [all_files[p]["priority_score"] for p in order]
        assert scores == sorted(scores, reverse=True)

    def test_reading_order_paths_exist_in_files(self, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        (tmp_plain / "pyproject.toml").write_text("[project]")
        manifest = scan_project(str(tmp_plain))
        file_paths = {f["path"] for f in manifest["files"]}
        for path in manifest["summary"]["reading_order"]:
            assert path in file_paths

    def test_entry_appears_first_in_reading_order(self, tmp_plain):
        """Entry point should come before plain source files."""
        (tmp_plain / "main.py").write_text("x")
        (tmp_plain / "utils.py").write_text("x")
        manifest = scan_project(str(tmp_plain))
        order = manifest["summary"]["reading_order"]
        assert order.index("main.py") < order.index("utils.py")
