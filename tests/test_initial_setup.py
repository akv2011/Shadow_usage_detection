"""
Initial setup tests for Shadow AI Detection Tool.

These tests verify that the project structure and basic configuration
are working correctly.
"""

import sys
from pathlib import Path


def test_project_initialization():
    """Test that the project initializes correctly."""
    assert True, "Basic assertion test passed"


def test_python_version():
    """Test that we're using a supported Python version."""
    assert sys.version_info >= (3, 9), f"Python 3.9+ required, got {sys.version}"


def test_project_structure():
    """Test that the required project directories exist."""
    project_root = Path(__file__).parent.parent

    # Check main directories exist
    assert (project_root / "shadow_ai").is_dir(), "shadow_ai directory missing"
    assert (project_root / "tests").is_dir(), "tests directory missing"
    assert (project_root / "docs").is_dir(), "docs directory missing"

    # Check essential files exist
    assert (project_root / "pyproject.toml").is_file(), "pyproject.toml missing"
    assert (project_root / ".gitignore").is_file(), ".gitignore missing"
    assert (project_root / "shadow_ai" / "__init__.py").is_file(), (
        "shadow_ai/__init__.py missing"
    )


def test_shadow_ai_import():
    """Test that the shadow_ai package can be imported."""
    import shadow_ai

    # Check package metadata exists
    assert hasattr(shadow_ai, "__version__"), "Package version not defined"
    assert hasattr(shadow_ai, "__author__"), "Package author not defined"

    # Check version format
    version = shadow_ai.__version__
    assert len(version.split(".")) >= 2, f"Invalid version format: {version}"


def test_configuration_files_exist():
    """Test that configuration files are present and accessible."""
    project_root = Path(__file__).parent.parent

    config_files = [
        "pyproject.toml",
        ".pre-commit-config.yaml",
        "dev.bat",
        "scripts/dev.ps1",
        "docs/environment.md",
    ]

    for config_file in config_files:
        file_path = project_root / config_file
        assert file_path.exists(), f"Configuration file missing: {config_file}"


def test_project_dependencies():
    """Test that core dependencies are available."""
    import importlib.util

    dependencies = ["fastapi", "uvicorn", "click", "pytest", "httpx"]

    for dep in dependencies:
        spec = importlib.util.find_spec(dep)
        if spec is None:
            raise AssertionError(f"Missing required dependency: {dep}")
def test_development_tools():
    """Test that development tools are accessible."""
    import subprocess

    # Test in shadow-ai conda environment
    conda_env = "shadow-ai"

    # Test ruff
    result = subprocess.run(
        ["conda", "run", "-n", conda_env, "ruff", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"ruff not accessible: {result.stderr}"
    assert "ruff" in result.stdout.lower(), "ruff version output unexpected"

    # Test mypy
    result = subprocess.run(
        ["conda", "run", "-n", conda_env, "mypy", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"mypy not accessible: {result.stderr}"
    assert "mypy" in result.stdout.lower(), "mypy version output unexpected"

    # Test pytest
    result = subprocess.run(
        ["conda", "run", "-n", conda_env, "pytest", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"pytest not accessible: {result.stderr}"
    assert "pytest" in result.stdout.lower(), "pytest version output unexpected"
