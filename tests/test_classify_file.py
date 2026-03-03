"""Tests for classify_file() in scan_project.py."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "document-everything" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from scan_project import classify_file


def _make(tmp_path, rel, content="x"):
    """Create a file and return (abs_path, rel_path)."""
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p, Path(rel)


class TestRequiredFields:
    def test_has_required_fields(self, tmp_plain):
        p, r = _make(tmp_plain, "main.py")
        result = classify_file(p, r)
        for field in ("path", "name", "size_bytes", "category", "language", "extension"):
            assert field in result

    def test_size_bytes_accurate(self, tmp_plain):
        content = "hello world"
        p, r = _make(tmp_plain, "main.py", content)
        result = classify_file(p, r)
        assert result["size_bytes"] == len(content.encode())

    def test_path_is_string(self, tmp_plain):
        p, r = _make(tmp_plain, "src/logic.py")
        result = classify_file(p, r)
        assert isinstance(result["path"], str)


class TestEntryPoints:
    @pytest.mark.parametrize("name", [
        "main.py", "app.py", "server.py", "index.py", "run.py", "start.py",
        "main.js", "index.js", "app.js", "server.js",
        "main.ts", "index.ts", "app.ts", "server.ts",
        "main.go", "main.rs", "__main__.py",
    ])
    def test_entry_names(self, tmp_plain, name):
        p, r = _make(tmp_plain, name)
        result = classify_file(p, r)
        assert result["category"] == "entry", f"{name} should be 'entry'"

    def test_entry_has_language(self, tmp_plain):
        p, r = _make(tmp_plain, "main.py")
        result = classify_file(p, r)
        assert result["language"] == "python"

    def test_entry_ts_language(self, tmp_plain):
        p, r = _make(tmp_plain, "server.ts")
        result = classify_file(p, r)
        assert result["language"] == "typescript"

    def test_entry_go_language(self, tmp_plain):
        p, r = _make(tmp_plain, "main.go")
        result = classify_file(p, r)
        assert result["language"] == "go"


class TestDocs:
    @pytest.mark.parametrize("name", [
        "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE.md",
        "DISCOVERY.md", "PLAN.md",
    ])
    def test_doc_names(self, tmp_plain, name):
        p, r = _make(tmp_plain, name)
        result = classify_file(p, r)
        assert result["category"] == "docs", f"{name} should be 'docs'"

    def test_arbitrary_md_is_docs(self, tmp_plain):
        p, r = _make(tmp_plain, "notes.md")
        result = classify_file(p, r)
        assert result["category"] == "docs"

    def test_rst_is_docs(self, tmp_plain):
        p, r = _make(tmp_plain, "guide.rst")
        result = classify_file(p, r)
        assert result["category"] == "docs"


class TestTests:
    @pytest.mark.parametrize("name", [
        "test_utils.py", "utils_test.py",
    ])
    def test_by_filename_pattern(self, tmp_plain, name):
        p, r = _make(tmp_plain, name)
        result = classify_file(p, r)
        assert result["category"] == "test"

    def test_spec_ts(self, tmp_plain):
        p, r = _make(tmp_plain, "utils.spec.ts")
        result = classify_file(p, r)
        assert result["category"] == "test"

    def test_inside_tests_dir(self, tmp_plain):
        p, r = _make(tmp_plain, "tests/helpers.py")
        result = classify_file(p, r)
        assert result["category"] == "test"

    def test_inside_spec_dir(self, tmp_plain):
        p, r = _make(tmp_plain, "spec/api.js")
        result = classify_file(p, r)
        assert result["category"] == "test"

    def test_test_has_language(self, tmp_plain):
        p, r = _make(tmp_plain, "tests/test_main.py")
        result = classify_file(p, r)
        assert result["language"] == "python"


class TestConfig:
    @pytest.mark.parametrize("name", [
        "pyproject.toml", "Makefile", "Dockerfile",
        ".env.example", "tsconfig.json", "vite.config.js",
        ".gitignore", "package.json",
    ])
    def test_config_names(self, tmp_plain, name):
        p, r = _make(tmp_plain, name)
        result = classify_file(p, r)
        assert result["category"] == "config", f"{name} should be 'config'"

    def test_yaml_extension_is_config(self, tmp_plain):
        p, r = _make(tmp_plain, "deploy.yaml")
        result = classify_file(p, r)
        assert result["category"] == "config"

    def test_toml_extension_is_config(self, tmp_plain):
        p, r = _make(tmp_plain, "config.toml")
        result = classify_file(p, r)
        assert result["category"] == "config"


class TestSource:
    @pytest.mark.parametrize("name,lang", [
        ("src/logic.py", "python"),
        ("service.ts", "typescript"),
        ("component.tsx", "typescript"),
        ("handler.go", "go"),
        ("lib.rs", "rust"),
    ])
    def test_source_files(self, tmp_plain, name, lang):
        p, r = _make(tmp_plain, name)
        result = classify_file(p, r)
        assert result["category"] == "source"
        assert result["language"] == lang

    def test_requirements_txt_is_docs(self, tmp_plain):
        """requirements.txt has .txt extension (in DOC_EXTENSIONS) so classified as docs."""
        p, r = _make(tmp_plain, "requirements.txt")
        result = classify_file(p, r)
        # .txt is in DOC_EXTENSIONS which is checked before CONFIG_NAMES
        assert result["category"] == "docs"

    def test_graphql_is_other(self, tmp_plain):
        p, r = _make(tmp_plain, "schema.graphql")
        result = classify_file(p, r)
        assert result["category"] == "other"
        assert result["language"] is None
