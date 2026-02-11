"""Unit tests for OutputParser class."""

import json
from typing import Any

import pytest

from repodoc.core.exceptions import OutputParseError, SchemaValidationError
from repodoc.core.parser import OutputParser
from repodoc.schemas.diet import DietOutput


@pytest.mark.unit
class TestOutputParser:
    """Tests for OutputParser class."""

    def test_parse_json_from_plain_json(self) -> None:
        """Test parsing JSON from plain JSON string."""
        parser = OutputParser()
        data = {"key": "value", "number": 42}
        json_str = json.dumps(data)

        result = parser.parse_json(json_str)

        assert result == data

    def test_parse_json_from_markdown_code_block(self) -> None:
        """Test parsing JSON from markdown code block."""
        parser = OutputParser()
        data = {"key": "value"}
        markdown = f"""
        Here's the result:

        ```json
        {json.dumps(data)}
        ```

        That's all!
        """

        result = parser.parse_json(markdown)

        assert result == data

    def test_parse_json_from_code_block_without_lang(self) -> None:
        """Test parsing JSON from code block without language."""
        parser = OutputParser()
        data = {"key": "value"}
        markdown = f"""
        ```
        {json.dumps(data)}
        ```
        """

        result = parser.parse_json(markdown)

        assert result == data

    def test_parse_json_multiple_blocks_uses_first(self) -> None:
        """Test that multiple JSON blocks uses the first one."""
        parser = OutputParser()
        first = {"first": True}
        second = {"second": True}
        markdown = f"""
        ```json
        {json.dumps(first)}
        ```

        ```json
        {json.dumps(second)}
        ```
        """

        result = parser.parse_json(markdown)

        assert result == first

    def test_parse_json_invalid_raises_error(self) -> None:
        """Test that invalid JSON raises OutputParseError."""
        parser = OutputParser()
        invalid_json = "This is not JSON at all!"

        with pytest.raises(OutputParseError):
            parser.parse_json(invalid_json)

    def test_parse_json_with_trailing_text(self) -> None:
        """Test parsing JSON with trailing non-JSON text."""
        parser = OutputParser()
        data = {"key": "value"}
        text = f"{json.dumps(data)}\n\nSome trailing explanation."

        # Should extract just the JSON part
        result = parser.parse_json(text)

        assert result == data

    def test_parse_and_validate_success(self, sample_diet_response: dict[str, Any]) -> None:
        """Test successful parse and validate."""
        parser = OutputParser()
        json_str = json.dumps(sample_diet_response)

        result = parser.parse_and_validate(json_str, DietOutput)

        assert isinstance(result, DietOutput)
        assert result.command == "diet"
        assert result.success is True

    def test_parse_and_validate_with_markdown(self, sample_diet_response: dict[str, Any]) -> None:
        """Test parse and validate with markdown wrapped JSON."""
        parser = OutputParser()
        markdown = f"""
        Here's your analysis:

        ```json
        {json.dumps(sample_diet_response)}
        ```
        """

        result = parser.parse_and_validate(markdown, DietOutput)

        assert isinstance(result, DietOutput)
        assert result.command == "diet"

    def test_parse_and_validate_invalid_json_raises(self) -> None:
        """Test that invalid JSON raises OutputParseError."""
        parser = OutputParser()

        with pytest.raises(OutputParseError):
            parser.parse_and_validate("Not JSON!", DietOutput)

    def test_parse_and_validate_wrong_schema_raises(self) -> None:
        """Test that wrong schema raises SchemaValidationError."""
        parser = OutputParser()
        # Valid JSON but wrong schema
        wrong_data = json.dumps({"command": "wrong", "data": "invalid"})

        with pytest.raises(SchemaValidationError):
            parser.parse_and_validate(wrong_data, DietOutput)

    def test_parse_and_validate_missing_required_field(self) -> None:
        """Test that missing required fields raises SchemaValidationError."""
        parser = OutputParser()
        incomplete_data = json.dumps(
            {
                "command": "diet",
                # Missing 'analysis' field which is required
            }
        )

        with pytest.raises(SchemaValidationError):
            parser.parse_and_validate(incomplete_data, DietOutput)

    def test_valid_json_can_be_parsed(self) -> None:
        """Test valid JSON can be parsed successfully."""
        parser = OutputParser()
        valid = json.dumps({"key": "value"})

        result = parser.parse_json(valid)
        assert result == {"key": "value"}

    def test_invalid_json_raises_error(self) -> None:
        """Test invalid JSON raises OutputParseError."""
        parser = OutputParser()

        with pytest.raises(OutputParseError):
            parser.parse_json("Not JSON")

        with pytest.raises(OutputParseError):
            parser.parse_json("{broken")

        with pytest.raises(OutputParseError):
            parser.parse_json("")

    def test_parse_with_extra_fields_allowed(self) -> None:
        """Test that extra fields in response don't break parsing."""
        parser = OutputParser()
        data = {
            "command": "diet",
            "success": True,
            "analysis": {
                "total_size_bytes": 1000,
                "total_size_human": "1 KB",
                "largest_files": [],
                "largest_directories": [],
                "suspected_artifacts": [],
                "missing_hygiene_files": [],
            },
            "diet_markdown": "# Test\n\nSome content",
            "extra_field": "This should be ignored",
        }

        result = parser.parse_and_validate(json.dumps(data), DietOutput)

        # Should parse successfully, ignoring extra field
        assert isinstance(result, DietOutput)
