"""Pytest fixtures for RepoDoctor tests."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create a temporary repository directory with sample files."""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    # Create sample Python files
    (repo / "main.py").write_text("print('Hello, world!')")
    (repo / "utils.py").write_text("def helper(): pass")

    # Create sample config files
    (repo / ".gitignore").write_text("*.pyc\n__pycache__/")
    (repo / "README.md").write_text("# Test Project")

    # Create a subdirectory
    src = repo / "src"
    src.mkdir()
    (src / "app.py").write_text("def main(): pass")

    return repo


@pytest.fixture
def empty_repo(tmp_path: Path) -> Path:
    """Create an empty repository directory."""
    repo = tmp_path / "empty_repo"
    repo.mkdir()
    return repo


@pytest.fixture
def sample_diet_response() -> dict[str, Any]:
    """Sample valid diet command response."""
    return {
        "command": "diet",
        "success": True,
        "analysis": {
            "total_size_bytes": 1500000,
            "total_size_human": "1.5 MB",
            "largest_files": [
                {"path": "dist/bundle.js", "size_bytes": 500000, "size_human": "500 KB"}
            ],
            "largest_directories": [
                {
                    "path": "node_modules",
                    "size_bytes": 1000000,
                    "size_human": "1 MB",
                    "file_count": 100,
                }
            ],
            "suspected_artifacts": ["dist/", "build/"],
            "missing_hygiene_files": [
                {
                    "filename": ".gitignore",
                    "importance": "Prevents committing build artifacts",
                    "template_url": None,
                },
                {
                    "filename": "LICENSE",
                    "importance": "Specifies project license",
                    "template_url": "https://choosealicense.com/",
                },
            ],
        },
        "issues": [
            {
                "title": "Large build artifacts committed",
                "description": "dist/ directory contains build artifacts",
                "severity": "high",
                "category": "bloat",
                "file_path": "dist/bundle.js",
                "suggestion": "Add dist/ to .gitignore",
            }
        ],
        "recommendations": [
            {
                "action": "Add .gitignore",
                "reason": "Prevent committing build artifacts",
                "priority": "high",
            }
        ],
        "metadata": {"timestamp": "2024-01-01T12:00:00Z", "copilot_version": "1.0.0"},
        "diet_markdown": (
            "# Repository Diet Analysis\n\n"
            "## Summary\n\nTotal Size: **1.5 MB**\n\n"
            "## Largest Files\n\n1. `dist/bundle.js` - 500 KB\n\n"
            "## Recommendations\n\n- Add .gitignore for build artifacts"
        ),
    }


@pytest.fixture
def sample_tour_response() -> dict[str, Any]:
    """Sample valid tour command response."""
    return {
        "command": "tour",
        "success": True,
        "tour": {
            "title": "Test Project Tour",
            "overview": "A simple test application",
            "tech_stack": ["Python 3.11", "pytest"],
            "entry_points": [
                {
                    "file": "main.py",
                    "description": "Application entry point",
                    "key_functions": ["main()"],
                }
            ],
            "key_directories": [
                {"path": "src/", "purpose": "Source code", "contains": ["Application logic"]}
            ],
            "architecture_notes": "Simple CLI application",
        },
        "tour_markdown": "# Test Project\n\nA simple test application.",
        "issues": [],
        "recommendations": [],
        "metadata": {"timestamp": "2024-01-01T12:00:00Z"},
    }


@pytest.fixture
def sample_docker_response() -> dict[str, Any]:
    """Sample valid docker command response."""
    return {
        "command": "docker",
        "success": True,
        "dockerfiles": [
            {
                "path": "Dockerfile",
                "base_image": "python:3.11-slim",
                "issues_found": 1,
                "security_score": 75,
            }
        ],
        "issues": [
            {
                "title": "Running as root",
                "description": "Container runs as root user",
                "severity": "medium",
                "category": "security",
                "file_path": "Dockerfile",
                "line_number": 10,
                "suggestion": "Add USER directive",
            }
        ],
        "recommendations": [
            {"action": "Add non-root user", "reason": "Improve container security"}
        ],
        "metadata": {"timestamp": "2024-01-01T12:00:00Z"},
    }


@pytest.fixture
def sample_deadcode_response() -> dict[str, Any]:
    """Sample valid deadcode command response."""
    return {
        "command": "deadcode",
        "success": True,
        "findings": [
            {
                "file_path": "src/unused.py",
                "item_name": "unused_function",
                "item_type": "function",
                "line_number": 10,
                "reason": "No references found in codebase",
                "confidence": "high",
            }
        ],
        "summary": {
            "total_findings": 1,
            "high_confidence": 1,
            "medium_confidence": 0,
            "low_confidence": 0,
        },
        "issues": [],
        "recommendations": [
            {"action": "Remove unused code", "reason": "Reduce maintenance burden"}
        ],
        "metadata": {"timestamp": "2024-01-01T12:00:00Z"},
    }


@pytest.fixture
def mock_copilot_success(
    monkeypatch: pytest.MonkeyPatch, sample_diet_response: dict[str, Any]
) -> None:
    """Mock successful Copilot CLI execution."""

    def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = json.dumps(sample_diet_response)
        result.stderr = ""
        return result

    import subprocess

    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def mock_copilot_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock failed Copilot CLI execution."""

    def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
        result = MagicMock()
        result.returncode = 1
        result.stdout = ""
        result.stderr = "Copilot CLI authentication failed"
        return result

    import subprocess

    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def mock_copilot_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock Copilot CLI timeout."""
    import subprocess

    def mock_run(*args: Any, **kwargs: Any) -> None:
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=120)

    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def mock_copilot_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock Copilot CLI not found."""
    import subprocess

    def mock_run(*args: Any, **kwargs: Any) -> None:
        raise FileNotFoundError("copilot command not found")

    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def mock_copilot_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock Copilot CLI returning invalid JSON."""

    def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
        result = MagicMock()
        result.returncode = 0
        result.stdout = "This is not JSON at all!"
        result.stderr = ""
        return result

    import subprocess

    monkeypatch.setattr(subprocess, "run", mock_run)
