"""Tests for prompt template loading."""

import pytest

from repodoc.prompts import get_prompt_loader


def test_prompt_loader_initialization() -> None:
    """Test that prompt loader initializes correctly."""
    loader = get_prompt_loader()
    assert loader.version == "v1"
    commands = loader.list_commands()
    assert len(commands) > 0


def test_load_diet_template() -> None:
    """Test loading the diet command template."""
    loader = get_prompt_loader()
    template = loader.get_template("diet")
    assert template.command == "diet"
    assert template.version == "v1"
    assert "bloat" in template.content.lower()
    assert "JSON" in template.content


def test_load_all_templates() -> None:
    """Test that all expected templates are loaded."""
    loader = get_prompt_loader()
    expected_commands = ["diet", "tour", "docker", "deadcode", "scan", "report"]
    commands = loader.list_commands()

    for expected in expected_commands:
        assert expected in commands, f"Missing template: {expected}"


def test_get_prompt_renders() -> None:
    """Test that get_prompt returns rendered string."""
    loader = get_prompt_loader()
    prompt = loader.get_prompt("diet")
    assert isinstance(prompt, str)
    assert len(prompt) > 100


def test_missing_template_raises() -> None:
    """Test that requesting non-existent template raises KeyError."""
    loader = get_prompt_loader()
    with pytest.raises(KeyError):
        loader.get_template("nonexistent")
