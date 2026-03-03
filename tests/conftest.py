"""Shared pytest fixtures for document-everything test suite."""

import importlib
import subprocess
import sys
import types
from pathlib import Path

import pytest


SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "document-everything" / "scripts"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_plain(tmp_path):
    """Non-git temp dir with .resolve() for macOS symlink safety."""
    return tmp_path.resolve()


@pytest.fixture
def tmp_git_repo(tmp_path):
    """Temp dir initialized as a git repo with test user config."""
    root = tmp_path.resolve()
    subprocess.run(["git", "init"], cwd=root, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=root, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=root, capture_output=True, check=True)
    return root


@pytest.fixture
def mcp_module():
    """
    Injects a fake mcp.server.fastmcp.FastMCP so mcp_server.py can be
    imported without the real 'mcp' package installed.
    """
    # Build minimal fake MCP hierarchy
    fake_mcp_pkg = types.ModuleType("mcp")
    fake_server = types.ModuleType("mcp.server")
    fake_fastmcp_mod = types.ModuleType("mcp.server.fastmcp")

    class FakeFastMCP:
        def __init__(self, name, instructions=""):
            self.name = name
            self.instructions = instructions
            self._tools = {}

        def tool(self):
            def decorator(fn):
                self._tools[fn.__name__] = fn
                return fn
            return decorator

        def run(self, transport="stdio", **kwargs):
            pass

    fake_fastmcp_mod.FastMCP = FakeFastMCP
    fake_mcp_pkg.server = fake_server
    fake_server.fastmcp = fake_fastmcp_mod

    # Inject into sys.modules before import
    sys.modules.setdefault("mcp", fake_mcp_pkg)
    sys.modules.setdefault("mcp.server", fake_server)
    sys.modules.setdefault("mcp.server.fastmcp", fake_fastmcp_mod)

    # Force fresh import of mcp_server
    mcp_server_path = str(SCRIPTS_DIR)
    if mcp_server_path not in sys.path:
        sys.path.insert(0, mcp_server_path)

    # Remove cached module if already imported
    for key in list(sys.modules.keys()):
        if "mcp_server" in key:
            del sys.modules[key]

    import mcp_server as mod
    return mod


def make_fake_manifest(root, size_class="small", project_type="generic",
                        files=None, reading_order=None, is_git=False):
    """Builder for a minimal manifest dict for patching scan_project() in MCP tests."""
    if files is None:
        files = []
    if reading_order is None:
        reading_order = []
    return {
        "root": str(root),
        "scanned_at": "2026-01-01T00:00:00+00:00",
        "is_git_repo": is_git,
        "git_remote": None,
        "files": files,
        "summary": {
            "total_files": len(files),
            "by_category": {},
            "languages": [],
            "source_file_count": 0,
            "size_class": size_class,
            "project_type": project_type,
            "reading_order": reading_order,
        },
    }
