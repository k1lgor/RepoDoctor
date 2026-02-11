"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from repodoc.schemas import (
    DietOutput,
    Issue,
    RepoHealthScore,
    Severity,
)


def test_issue_schema() -> None:
    """Test Issue schema validation."""
    issue = Issue(
        title="Large build artifact committed",
        description="dist/ directory is 50MB and should be in .gitignore",
        severity=Severity.HIGH,
        category="bloat",
        file_path="dist/bundle.js",
        suggestion="Add dist/ to .gitignore and remove from git",
    )
    assert issue.title == "Large build artifact committed"
    assert issue.severity == Severity.HIGH


def test_repo_health_score() -> None:
    """Test RepoHealthScore validation."""
    score = RepoHealthScore(
        overall_score=75, category_scores={"bloat": 80, "security": 70}, grade="B"
    )
    assert score.is_healthy
    assert score.overall_score == 75


def test_diet_output_schema() -> None:
    """Test DietOutput schema can be instantiated."""
    output = DietOutput(
        command="diet",
        analysis={
            "total_size_bytes": 1000000,
            "total_size_human": "1 MB",
            "largest_files": [],
            "largest_directories": [],
            "suspected_artifacts": [],
            "missing_hygiene_files": [],
        },
        diet_markdown="# Repository Diet Analysis\n\nTest content",
    )
    assert output.command == "diet"
    assert output.success is True


def test_invalid_severity() -> None:
    """Test that invalid severity values are rejected."""
    with pytest.raises(ValidationError):
        Issue(
            title="Test",
            description="Test",
            severity="invalid",  # type: ignore
            category="test",
        )
