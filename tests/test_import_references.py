"""Tests for _resolve_relative_import and compute_import_references."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "document-everything" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
FIXTURES_DIR = Path(__file__).parent / "fixtures"

from scan_project import _resolve_relative_import, compute_import_references


class TestResolveRelativeImportPython:
    def test_basic_relative_import(self, tmp_plain):
        """from .helpers import x → resolves to helpers.py in same dir."""
        helpers = tmp_plain / "helpers.py"
        helpers.write_text("def x(): pass")
        importer = tmp_plain / "main.py"
        result = _resolve_relative_import(importer, ".helpers", tmp_plain)
        assert result == "helpers.py"

    def test_nested_relative_import(self, tmp_plain):
        """from .utils.helpers import x → resolves to utils/helpers.py."""
        (tmp_plain / "utils").mkdir()
        (tmp_plain / "utils" / "helpers.py").write_text("def x(): pass")
        importer = tmp_plain / "main.py"
        result = _resolve_relative_import(importer, ".utils.helpers", tmp_plain)
        assert result == "utils/helpers.py"

    def test_directory_does_not_shadow_py_file(self, tmp_plain):
        """A directory named 'utils' should not shadow utils.py (Bug 1 fix)."""
        (tmp_plain / "utils").mkdir()
        (tmp_plain / "utils.py").write_text("x = 1")
        importer = tmp_plain / "main.py"
        result = _resolve_relative_import(importer, ".utils", tmp_plain)
        # Should return utils.py (the file), not just "utils" (the directory)
        assert result == "utils.py"

    def test_resolves_package_init(self, tmp_plain):
        """from .pkg import x → resolves to pkg/__init__.py if pkg/ has __init__.py."""
        (tmp_plain / "pkg").mkdir()
        (tmp_plain / "pkg" / "__init__.py").write_text("x = 1")
        importer = tmp_plain / "main.py"
        result = _resolve_relative_import(importer, ".pkg", tmp_plain)
        assert result == "pkg/__init__.py"

    def test_nonexistent_returns_none(self, tmp_plain):
        """Import to a file that doesn't exist → None."""
        importer = tmp_plain / "main.py"
        result = _resolve_relative_import(importer, ".nonexistent", tmp_plain)
        assert result is None

    def test_outside_root_returns_none(self, tmp_plain):
        """Import that escapes root dir → None."""
        (tmp_plain / "main.py").write_text("")
        importer = tmp_plain / "main.py"
        result = _resolve_relative_import(importer, "....outside", tmp_plain)
        assert result is None


class TestResolveRelativeImportJS:
    def test_dotslash_import(self, tmp_plain):
        """import x from './utils' → resolves to utils.js (Bug 2 fix)."""
        (tmp_plain / "utils.js").write_text("export const x = 1;")
        importer = tmp_plain / "index.js"
        result = _resolve_relative_import(importer, "./utils", tmp_plain)
        assert result == "utils.js"

    def test_dotslash_subdir(self, tmp_plain):
        """import x from './lib/utils' → resolves to lib/utils.js."""
        (tmp_plain / "lib").mkdir()
        (tmp_plain / "lib" / "utils.js").write_text("export const x = 1;")
        importer = tmp_plain / "index.js"
        result = _resolve_relative_import(importer, "./lib/utils", tmp_plain)
        assert result == "lib/utils.js"

    def test_dotdotslash_import(self, tmp_plain):
        """import x from '../utils' → resolves to utils.js one level up."""
        (tmp_plain / "utils.js").write_text("export const x = 1;")
        (tmp_plain / "src").mkdir()
        importer = tmp_plain / "src" / "main.js"
        result = _resolve_relative_import(importer, "../utils", tmp_plain)
        assert result == "utils.js"

    def test_dotslash_not_absolute(self, tmp_plain):
        """'./utils' should NOT produce an absolute /utils path (Bug 2 fix)."""
        # If bug 2 exists, this would try to open /utils.js and fail
        (tmp_plain / "utils.js").write_text("x")
        importer = tmp_plain / "index.js"
        result = _resolve_relative_import(importer, "./utils", tmp_plain)
        # Result should be repo-relative, not None (would be None if absolute path bug hit)
        assert result is not None
        assert not result.startswith("/")

    def test_js_index_resolution(self, tmp_plain):
        """import x from './lib' → resolves to lib/index.js."""
        (tmp_plain / "lib").mkdir()
        (tmp_plain / "lib" / "index.js").write_text("export default {};")
        importer = tmp_plain / "index.js"
        result = _resolve_relative_import(importer, "./lib", tmp_plain)
        assert result == "lib/index.js"

    def test_nonexistent_js_returns_none(self, tmp_plain):
        importer = tmp_plain / "index.js"
        result = _resolve_relative_import(importer, "./nonexistent", tmp_plain)
        assert result is None


class TestComputeImportReferences:
    def test_python_fixture(self):
        """python_pkg fixture: helpers.py is imported by main.py and models.py."""
        root = FIXTURES_DIR / "python_pkg"
        files = [
            {"path": "main.py", "category": "entry", "language": "python"},
            {"path": "models.py", "category": "source", "language": "python"},
            {"path": "utils/helpers.py", "category": "source", "language": "python"},
            {"path": "utils/__init__.py", "category": "source", "language": "python"},
        ]
        result = compute_import_references(files, root)
        assert isinstance(result, dict)
        # helpers.py should be referenced
        assert result.get("utils/helpers.py", 0) >= 1

    def test_js_fixture(self):
        """js_app fixture: lib/utils.js is imported by index.js."""
        root = FIXTURES_DIR / "js_app"
        files = [
            {"path": "index.js", "category": "entry", "language": "javascript"},
            {"path": "lib/utils.js", "category": "source", "language": "javascript"},
        ]
        result = compute_import_references(files, root)
        assert result.get("lib/utils.js", 0) >= 1

    def test_self_import_not_counted(self, tmp_plain):
        """A file importing itself should not increment its own count."""
        f = tmp_plain / "self.py"
        f.write_text("from .self import thing")
        files = [{"path": "self.py", "category": "source", "language": "python"}]
        result = compute_import_references(files, tmp_plain)
        assert result.get("self.py", 0) == 0

    def test_unsupported_language_not_scanned(self, tmp_plain):
        """Ruby files are not scanned for imports."""
        f = tmp_plain / "main.rb"
        f.write_text("require_relative 'utils'")
        files = [{"path": "main.rb", "category": "source", "language": "ruby"}]
        result = compute_import_references(files, tmp_plain)
        assert result == {}

    def test_missing_file_no_crash(self, tmp_plain):
        """If the source file doesn't exist on disk, no crash."""
        files = [{"path": "missing.py", "category": "source", "language": "python"}]
        result = compute_import_references(files, tmp_plain)
        assert isinstance(result, dict)

    def test_returns_plain_dict(self, tmp_plain):
        """Result is a plain dict, not defaultdict."""
        from collections import defaultdict
        result = compute_import_references([], tmp_plain)
        assert type(result) is dict
        assert not isinstance(result, defaultdict)
