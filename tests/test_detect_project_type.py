"""Tests for detect_project_type() in scan_project.py."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "document-everything" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
FIXTURES_DIR = Path(__file__).parent / "fixtures"

from scan_project import detect_project_type


def _files(*names):
    """Build a minimal files list from file names."""
    result = []
    for name in names:
        p = Path(name)
        result.append({
            "name": p.name,
            "path": name,
            "extension": p.suffix.lower(),
            "category": "source",
            "language": None,
        })
    return result


class TestNextflow:
    def test_nf_extension(self, tmp_plain):
        (tmp_plain / "main.nf").touch()
        result = detect_project_type(_files("main.nf"), tmp_plain)
        assert result == "nextflow"

    def test_nextflow_config(self, tmp_plain):
        (tmp_plain / "nextflow.config").touch()
        result = detect_project_type(_files("nextflow.config"), tmp_plain)
        assert result == "nextflow"

    def test_fixture(self):
        root = FIXTURES_DIR / "nextflow_project"
        files = _files("main.nf", "nextflow.config")
        result = detect_project_type(files, root)
        assert result == "nextflow"


class TestFrontend:
    @pytest.mark.parametrize("name", [
        "vite.config.js", "vite.config.ts", "next.config.js",
        "angular.json", "nuxt.config.ts",
    ])
    def test_frontend_configs(self, tmp_plain, name):
        (tmp_plain / name).touch()
        result = detect_project_type(_files(name), tmp_plain)
        assert result == "frontend"

    def test_fixture(self):
        root = FIXTURES_DIR / "frontend_app"
        files = _files("vite.config.ts", "src/main.ts")
        result = detect_project_type(files, root)
        assert result == "frontend"


class TestRestApi:
    @pytest.mark.parametrize("name", ["openapi.yaml", "swagger.yml", "routes.py"])
    def test_api_signals(self, tmp_plain, name):
        (tmp_plain / name).touch()
        result = detect_project_type(_files(name), tmp_plain)
        assert result == "rest-api"

    def test_fixture(self):
        root = FIXTURES_DIR / "rest_api"
        files = _files("app.py", "openapi.yaml", "controllers/users.py")
        result = detect_project_type(files, root)
        assert result == "rest-api"

    def test_disambiguation_library_with_controllers(self, tmp_plain):
        """pyproject.toml + controllers/ dir → rest-api, not library."""
        (tmp_plain / "pyproject.toml").touch()
        (tmp_plain / "controllers").mkdir()
        files = _files("pyproject.toml")
        result = detect_project_type(files, tmp_plain)
        assert result == "rest-api"


class TestCli:
    @pytest.mark.parametrize("name", ["cli.py", "cli.js", "cli.ts"])
    def test_cli_entry(self, tmp_plain, name):
        (tmp_plain / name).touch()
        result = detect_project_type(_files(name), tmp_plain)
        assert result == "cli"

    def test_commands_dir(self, tmp_plain):
        (tmp_plain / "commands").mkdir()
        result = detect_project_type([], tmp_plain)
        assert result == "cli"

    def test_fixture(self):
        root = FIXTURES_DIR / "cli_project"
        files = _files("cli.py", "commands/build.py")
        result = detect_project_type(files, root)
        assert result == "cli"


class TestDataPipeline:
    @pytest.mark.parametrize("name", ["dbt_project.yml", "airflow.cfg", "prefect.yaml"])
    def test_pipeline_signals(self, tmp_plain, name):
        (tmp_plain / name).touch()
        result = detect_project_type(_files(name), tmp_plain)
        assert result == "data-pipeline"

    def test_dags_dir(self, tmp_plain):
        (tmp_plain / "dags").mkdir()
        result = detect_project_type([], tmp_plain)
        assert result == "data-pipeline"

    def test_fixture(self):
        root = FIXTURES_DIR / "data_pipeline"
        files = _files("dbt_project.yml", "dags/etl.py")
        result = detect_project_type(files, root)
        assert result == "data-pipeline"


class TestLibrary:
    @pytest.mark.parametrize("name", ["pyproject.toml", "Cargo.toml", "setup.py"])
    def test_library_signals(self, tmp_plain, name):
        (tmp_plain / name).touch()
        result = detect_project_type(_files(name), tmp_plain)
        assert result == "library"

    def test_fixture(self):
        root = FIXTURES_DIR / "library_pkg"
        files = _files("pyproject.toml", "src/mylib/__init__.py")
        result = detect_project_type(files, root)
        assert result == "library"


class TestGeneric:
    def test_empty_project(self, tmp_plain):
        result = detect_project_type([], tmp_plain)
        assert result == "generic"

    def test_single_main_py(self, tmp_plain):
        """Single main.py has no strong signal → generic."""
        (tmp_plain / "main.py").touch()
        result = detect_project_type(_files("main.py"), tmp_plain)
        assert result == "generic"

    def test_index_html_alone(self, tmp_plain):
        """index.html is only a booster, not a required signal."""
        (tmp_plain / "index.html").touch()
        result = detect_project_type(_files("index.html"), tmp_plain)
        assert result == "generic"


class TestConflictResolution:
    def test_vite_beats_pyproject(self, tmp_plain):
        """vite.config.ts + pyproject.toml → frontend wins (higher score)."""
        (tmp_plain / "vite.config.ts").touch()
        (tmp_plain / "pyproject.toml").touch()
        files = _files("vite.config.ts", "pyproject.toml")
        result = detect_project_type(files, tmp_plain)
        assert result == "frontend"
