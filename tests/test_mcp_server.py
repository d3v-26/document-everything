"""Tests for MCP tools: scan_repo, generate_wiki, ask_repo."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "document-everything" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Import make_fake_manifest from conftest
sys.path.insert(0, str(Path(__file__).parent))
from conftest import make_fake_manifest


class TestScanRepo:
    def test_valid_path_returns_json(self, mcp_module, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        result = mcp_module.scan_repo(str(tmp_plain))
        data = json.loads(result)
        for key in ("root", "files", "summary"):
            assert key in data

    def test_empty_path_uses_cwd(self, mcp_module, monkeypatch, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        monkeypatch.chdir(tmp_plain)
        result = mcp_module.scan_repo("")
        data = json.loads(result)
        assert data["root"] == str(tmp_plain)

    def test_nonexistent_path_returns_error_json(self, mcp_module):
        result = mcp_module.scan_repo("/tmp/nonexistent_path_xyz_abc_123")
        data = json.loads(result)
        assert "error" in data

    def test_file_categories_are_valid(self, mcp_module, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        (tmp_plain / "utils.py").write_text("x")
        result = mcp_module.scan_repo(str(tmp_plain))
        data = json.loads(result)
        valid_cats = {"entry", "source", "config", "test", "docs", "other"}
        for f in data["files"]:
            assert f["category"] in valid_cats


class TestGenerateWiki:
    def _fake_manifest(self, root, size_class="small", project_type="generic",
                        reading_order=None):
        return make_fake_manifest(
            root, size_class=size_class, project_type=project_type,
            reading_order=reading_order or [],
            files=[{"path": "main.py", "category": "entry", "priority_score": 100}],
        )

    def test_returns_string(self, mcp_module, tmp_plain):
        with patch("mcp_server.scan_project", return_value=self._fake_manifest(tmp_plain)):
            result = mcp_module.generate_wiki(str(tmp_plain))
        assert isinstance(result, str)

    def test_contains_manifest_json_block(self, mcp_module, tmp_plain):
        with patch("mcp_server.scan_project", return_value=self._fake_manifest(tmp_plain)):
            result = mcp_module.generate_wiki(str(tmp_plain))
        assert "```json" in result

    def test_small_output_location(self, mcp_module, tmp_plain):
        with patch("mcp_server.scan_project", return_value=self._fake_manifest(tmp_plain, "small")):
            result = mcp_module.generate_wiki(str(tmp_plain))
        assert "PROJECT_DOCS.md" in result

    def test_medium_output_location(self, mcp_module, tmp_plain):
        with patch("mcp_server.scan_project", return_value=self._fake_manifest(tmp_plain, "medium")):
            result = mcp_module.generate_wiki(str(tmp_plain))
        assert "docs/overview.md" in result

    def test_large_output_location(self, mcp_module, tmp_plain):
        with patch("mcp_server.scan_project", return_value=self._fake_manifest(tmp_plain, "large")):
            result = mcp_module.generate_wiki(str(tmp_plain))
        assert "docs/modules" in result

    def test_deep_false_includes_mermaid(self, mcp_module, tmp_plain):
        with patch("mcp_server.scan_project", return_value=self._fake_manifest(tmp_plain)):
            result = mcp_module.generate_wiki(str(tmp_plain), deep=False)
        assert "Mermaid" in result or "mermaid" in result.lower()
        assert "3" in result  # "3–5 Mermaid diagrams"

    def test_deep_true_includes_deep_mode(self, mcp_module, tmp_plain):
        with patch("mcp_server.scan_project", return_value=self._fake_manifest(tmp_plain)):
            result = mcp_module.generate_wiki(str(tmp_plain), deep=True)
        assert "DEEP MODE" in result

    def test_shows_top_10_of_reading_order(self, mcp_module, tmp_plain):
        order = [f"file{i}.py" for i in range(15)]
        manifest = self._fake_manifest(tmp_plain, reading_order=order)
        with patch("mcp_server.scan_project", return_value=manifest):
            result = mcp_module.generate_wiki(str(tmp_plain))
        # The Instructions section lists top 10 files with "  - " prefix
        assert "  - file9.py" in result   # 10th file shown in instructions
        assert "  - file10.py" not in result  # 11th file not in instructions listing

    def test_bad_path_returns_error(self, mcp_module):
        result = mcp_module.generate_wiki("/tmp/nonexistent_xyz_abc_123")
        assert "ERROR" in result

    def test_unknown_size_class_fallback(self, mcp_module, tmp_plain):
        manifest = self._fake_manifest(tmp_plain, size_class="unknown")
        with patch("mcp_server.scan_project", return_value=manifest):
            result = mcp_module.generate_wiki(str(tmp_plain))
        assert "PROJECT_DOCS.md" in result

    def test_project_type_in_instructions(self, mcp_module, tmp_plain):
        manifest = self._fake_manifest(tmp_plain, project_type="rest-api")
        with patch("mcp_server.scan_project", return_value=manifest):
            result = mcp_module.generate_wiki(str(tmp_plain))
        assert "rest-api" in result


class TestAskRepo:
    def _fake_manifest_with_files(self, root):
        files = [
            {"path": "auth/login.py", "category": "source", "priority_score": 80},
            {"path": "auth/middleware.py", "category": "source", "priority_score": 70},
            {"path": "utils/helpers.py", "category": "source", "priority_score": 50},
            {"path": "main.py", "category": "entry", "priority_score": 100},
        ]
        return make_fake_manifest(
            root,
            files=files,
            reading_order=["main.py", "auth/login.py", "auth/middleware.py", "utils/helpers.py"],
        )

    def test_returns_string(self, mcp_module, tmp_plain):
        with patch("mcp_server.scan_project", return_value=self._fake_manifest_with_files(tmp_plain)):
            result = mcp_module.ask_repo("how does authentication work?", str(tmp_plain))
        assert isinstance(result, str)

    def test_question_included_verbatim(self, mcp_module, tmp_plain):
        q = "how does authentication work?"
        with patch("mcp_server.scan_project", return_value=self._fake_manifest_with_files(tmp_plain)):
            result = mcp_module.ask_repo(q, str(tmp_plain))
        assert q in result

    def test_auth_keyword_ranks_auth_files_higher(self, mcp_module, tmp_plain):
        """'auth' keyword → auth files should appear before utils/helpers.py."""
        with patch("mcp_server.scan_project", return_value=self._fake_manifest_with_files(tmp_plain)):
            result = mcp_module.ask_repo("how does auth login work?", str(tmp_plain))
        auth_pos = result.find("auth/login.py")
        helpers_pos = result.find("utils/helpers.py")
        # auth files should appear before or equal to helpers (due to keyword match)
        if auth_pos != -1 and helpers_pos != -1:
            assert auth_pos <= helpers_pos

    def test_test_and_docs_excluded(self, mcp_module, tmp_plain):
        """Test and docs files should not appear in ask_repo results."""
        manifest = make_fake_manifest(
            tmp_plain,
            files=[
                {"path": "main.py", "category": "entry", "priority_score": 100},
                {"path": "test_main.py", "category": "test", "priority_score": 10},
                {"path": "README.md", "category": "docs", "priority_score": 20},
            ],
            reading_order=["main.py"],
        )
        with patch("mcp_server.scan_project", return_value=manifest):
            result = mcp_module.ask_repo("what does this do?", str(tmp_plain))
        assert "test_main.py" not in result
        assert "README.md" not in result

    def test_at_most_15_files_returned(self, mcp_module, tmp_plain):
        """Result should contain at most 15 files."""
        files = [
            {"path": f"src/file{i}.py", "category": "source", "priority_score": 50}
            for i in range(20)
        ]
        reading_order = [f["path"] for f in files]
        manifest = make_fake_manifest(tmp_plain, files=files, reading_order=reading_order)
        with patch("mcp_server.scan_project", return_value=manifest):
            result = mcp_module.ask_repo("how does this work?", str(tmp_plain))
        file_mentions = [f"src/file{i}.py" for i in range(20)]
        count = sum(1 for name in file_mentions if name in result)
        assert count <= 15

    def test_all_stopword_question_still_returns_files(self, mcp_module, tmp_plain):
        """All-stopword question should still return files ranked by priority."""
        with patch("mcp_server.scan_project", return_value=self._fake_manifest_with_files(tmp_plain)):
            result = mcp_module.ask_repo("what is the", str(tmp_plain))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_bad_path_returns_error(self, mcp_module):
        result = mcp_module.ask_repo("anything", "/tmp/nonexistent_xyz_abc_123")
        assert "ERROR" in result

    def test_empty_path_no_error(self, mcp_module, monkeypatch, tmp_plain):
        (tmp_plain / "main.py").write_text("x")
        monkeypatch.chdir(tmp_plain)
        result = mcp_module.ask_repo("what does this do?", "")
        assert "ERROR" not in result
