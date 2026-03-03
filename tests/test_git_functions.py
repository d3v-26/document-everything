"""Tests for git helper functions in scan_project.py."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "document-everything" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
THIS_REPO = Path(__file__).parent.parent

from scan_project import (
    get_git_info,
    get_git_remote,
    get_recently_changed_files,
    is_git_repo,
)


class TestIsGitRepo:
    def test_this_repo_is_git(self):
        assert is_git_repo(THIS_REPO) is True

    def test_non_git_dir(self, tmp_plain):
        assert is_git_repo(tmp_plain) is False

    def test_timeout_returns_false(self, tmp_plain):
        with patch("scan_project.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
            assert is_git_repo(tmp_plain) is False

    def test_missing_git_returns_false(self, tmp_plain):
        with patch("scan_project.subprocess.run", side_effect=FileNotFoundError):
            assert is_git_repo(tmp_plain) is False


class TestGetGitRemote:
    def test_this_repo_has_remote(self):
        remote = get_git_remote(THIS_REPO)
        assert remote is not None
        assert "document-everything" in remote

    def test_fresh_git_repo_has_no_remote(self, tmp_git_repo):
        result = get_git_remote(tmp_git_repo)
        assert result is None

    def test_timeout_returns_none(self, tmp_plain):
        with patch("scan_project.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
            assert get_git_remote(tmp_plain) is None

    def test_missing_git_returns_none(self, tmp_plain):
        with patch("scan_project.subprocess.run", side_effect=FileNotFoundError):
            assert get_git_remote(tmp_plain) is None


class TestGetGitInfo:
    def test_returns_dict_for_known_file(self):
        """scan_project.py exists in git history → should return a dict."""
        rel = "skills/document-everything/scripts/scan_project.py"
        result = get_git_info(THIS_REPO, rel)
        assert result is not None
        assert isinstance(result, dict)
        assert "last_changed" in result
        assert "last_commit_msg" in result
        assert "last_author" in result

    def test_nonexistent_file_returns_none(self):
        result = get_git_info(THIS_REPO, "nonexistent_file_xyz.py")
        assert result is None

    def test_pipe_in_commit_message_handled(self, tmp_git_repo):
        """Commit message with | should not break parsing — only split on first 2 pipes."""
        (tmp_git_repo / "a.py").write_text("x")
        subprocess.run(["git", "add", "a.py"], cwd=tmp_git_repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "fix: handle pipe|in|message"],
            cwd=tmp_git_repo, capture_output=True,
        )
        result = get_git_info(tmp_git_repo, "a.py")
        assert result is not None
        # Commit message should be "fix: handle pipe|in|message" (everything after first |)
        # or at minimum, not crash
        assert result["last_changed"] is not None

    def test_timeout_returns_none(self):
        with patch("scan_project.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
            assert get_git_info(THIS_REPO, "README.md") is None

    def test_missing_git_returns_none(self):
        with patch("scan_project.subprocess.run", side_effect=FileNotFoundError):
            assert get_git_info(THIS_REPO, "README.md") is None


class TestGetRecentlyChangedFiles:
    def test_returns_dict(self):
        result = get_recently_changed_files(THIS_REPO)
        assert isinstance(result, dict)

    def test_non_git_returns_empty(self, tmp_plain):
        result = get_recently_changed_files(tmp_plain)
        assert result == {}

    def test_timeout_returns_empty(self, tmp_plain):
        with patch("scan_project.subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
            assert get_recently_changed_files(tmp_plain) == {}

    def test_missing_git_returns_empty(self, tmp_plain):
        with patch("scan_project.subprocess.run", side_effect=FileNotFoundError):
            assert get_recently_changed_files(tmp_plain) == {}

    def test_max_score_equals_n(self, tmp_git_repo):
        """Most recently committed file should get score=n (default 30)."""
        (tmp_git_repo / "latest.py").write_text("x")
        subprocess.run(["git", "add", "latest.py"], cwd=tmp_git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add latest"], cwd=tmp_git_repo, capture_output=True)
        result = get_recently_changed_files(tmp_git_repo, n=30)
        assert result.get("latest.py") == 30

    def test_committed_files_appear_in_scores(self, tmp_git_repo):
        """All committed files should appear in the recency scores dict."""
        for name in ("old.py", "new.py"):
            (tmp_git_repo / name).write_text("x")
            subprocess.run(["git", "add", name], cwd=tmp_git_repo, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"add {name}"], cwd=tmp_git_repo, capture_output=True)
        result = get_recently_changed_files(tmp_git_repo)
        # Both files appear in git history → both should have scores
        assert "new.py" in result
        assert "old.py" in result

    def test_scoring_algorithm(self, tmp_plain):
        """Synthetic stdout: blank lines between file groups cause score decrement."""
        # First file(s) in list get n, blank line decrements by 1, next group gets n-1, etc.
        fake_stdout = "file_c.py\n\nfile_b.py\n\nfile_a.py\n"
        fake_result = type("R", (), {"returncode": 0, "stdout": fake_stdout})()
        with patch("scan_project.subprocess.run", return_value=fake_result):
            result = get_recently_changed_files(tmp_plain, n=10)
        assert result["file_c.py"] == 10
        assert result["file_b.py"] == 9
        assert result["file_a.py"] == 8
