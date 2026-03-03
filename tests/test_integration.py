"""Integration tests: end-to-end against this repo and fixture repos."""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "document-everything" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
THIS_REPO = Path(__file__).parent.parent.resolve()
FIXTURES_DIR = Path(__file__).parent / "fixtures"

from scan_project import scan_project


class TestSelfScan:
    def test_completes_without_error(self):
        result = scan_project(str(THIS_REPO))
        assert isinstance(result, dict)

    def test_is_git_true(self):
        result = scan_project(str(THIS_REPO))
        assert result["is_git_repo"] is True

    def test_remote_contains_project_name(self):
        result = scan_project(str(THIS_REPO))
        remote = result.get("git_remote") or ""
        assert "document-everything" in remote

    def test_finds_scan_project_py(self):
        result = scan_project(str(THIS_REPO))
        paths = {f["path"] for f in result["files"]}
        assert "skills/document-everything/scripts/scan_project.py" in paths

    def test_finds_mcp_server_py(self):
        result = scan_project(str(THIS_REPO))
        paths = {f["path"] for f in result["files"]}
        assert "skills/document-everything/scripts/mcp_server.py" in paths

    def test_reading_order_nonempty(self):
        result = scan_project(str(THIS_REPO))
        assert len(result["summary"]["reading_order"]) > 0

    def test_dist_contents_excluded(self):
        result = scan_project(str(THIS_REPO))
        paths = {f["path"] for f in result["files"]}
        assert not any(p.startswith("dist/") for p in paths)

    def test_scan_project_has_recency_bonus(self):
        """scan_project.py was recently modified → priority_score > 50 (source base)."""
        result = scan_project(str(THIS_REPO))
        target = next(
            (f for f in result["files"]
             if f["path"] == "skills/document-everything/scripts/scan_project.py"),
            None,
        )
        assert target is not None
        assert target["priority_score"] > 50


class TestFixtureScans:
    @pytest.mark.parametrize("fixture,expected_type", [
        ("nextflow_project", "nextflow"),
        ("rest_api", "rest-api"),
        ("library_pkg", "library"),
        ("data_pipeline", "data-pipeline"),
        ("cli_project", "cli"),
        ("frontend_app", "frontend"),
    ])
    def test_project_type_detection(self, fixture, expected_type):
        root = FIXTURES_DIR / fixture
        result = scan_project(str(root))
        assert result["summary"]["project_type"] == expected_type, (
            f"{fixture}: expected '{expected_type}', got '{result['summary']['project_type']}'"
        )

    def test_rest_api_app_py_is_entry(self):
        result = scan_project(str(FIXTURES_DIR / "rest_api"))
        f = next((x for x in result["files"] if x["name"] == "app.py"), None)
        assert f is not None
        assert f["category"] == "entry"

    def test_rest_api_pyproject_is_config(self):
        result = scan_project(str(FIXTURES_DIR / "library_pkg"))
        f = next((x for x in result["files"] if x["name"] == "pyproject.toml"), None)
        assert f is not None
        assert f["category"] == "config"

    def test_frontend_vite_config_is_config(self):
        result = scan_project(str(FIXTURES_DIR / "frontend_app"))
        f = next((x for x in result["files"] if x["name"] == "vite.config.ts"), None)
        assert f is not None
        assert f["category"] == "config"

    def test_cli_cli_py_is_source(self):
        """cli.py is not in ENTRY_NAMES, so it's classified as 'source'."""
        result = scan_project(str(FIXTURES_DIR / "cli_project"))
        f = next((x for x in result["files"] if x["name"] == "cli.py"), None)
        assert f is not None
        assert f["category"] == "source"


class TestGitIntegration:
    def test_newer_commit_higher_score(self, tmp_git_repo):
        """main.py committed last → higher score than utils.py committed first."""
        (tmp_git_repo / "utils.py").write_text("def x(): pass")
        subprocess.run(["git", "add", "utils.py"], cwd=tmp_git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add utils"], cwd=tmp_git_repo, capture_output=True)

        (tmp_git_repo / "main.py").write_text("from .utils import x")
        subprocess.run(["git", "add", "main.py"], cwd=tmp_git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add main"], cwd=tmp_git_repo, capture_output=True)

        result = scan_project(str(tmp_git_repo))
        files = {f["path"]: f for f in result["files"]}

        # main.py is an entry point (base=100) AND more recently committed
        # utils.py is source (base=50) AND older
        assert files["main.py"]["priority_score"] > files["utils.py"]["priority_score"]

    def test_three_commits_all_appear_in_reading_order(self, tmp_git_repo):
        """Three commits: all files appear in reading_order."""
        for name in ("a.py", "b.py", "c.py"):
            (tmp_git_repo / name).write_text(f"# {name}")
            subprocess.run(["git", "add", name], cwd=tmp_git_repo, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"add {name}"], cwd=tmp_git_repo, capture_output=True)

        result = scan_project(str(tmp_git_repo))
        order = result["summary"]["reading_order"]
        assert set(order) == {"a.py", "b.py", "c.py"}

    def test_uncommitted_file_has_no_last_changed(self, tmp_git_repo):
        """An uncommitted file should not have last_changed in its metadata."""
        (tmp_git_repo / "untracked.py").write_text("x")
        result = scan_project(str(tmp_git_repo))
        f = next((x for x in result["files"] if x["path"] == "untracked.py"), None)
        assert f is not None
        assert "last_changed" not in f
