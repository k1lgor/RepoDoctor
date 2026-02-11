"""Output parsing and validation module."""

import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from repodoc.core.exceptions import OutputParseError, SchemaValidationError
from repodoc.core.logger import get_logger

T = TypeVar("T", bound=BaseModel)


class OutputParser:
    """Parses and validates Copilot CLI output against Pydantic schemas."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def extract_json(self, raw_output: str) -> str:
        """
        Extract JSON from raw output, handling markdown code blocks.

        Args:
            raw_output: Raw output from Copilot CLI

        Returns:
            Extracted JSON string

        Raises:
            OutputParseError: If JSON cannot be extracted
        """
        # Try to find JSON in markdown code blocks first
        json_block_pattern = r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```"
        matches = re.findall(json_block_pattern, raw_output, re.DOTALL)

        if matches:
            self.logger.debug("Found JSON in markdown code block")
            return matches[0]

        # Try to find raw JSON (object or array)
        json_pattern = r"(\{.*\}|\[.*\])"
        matches = re.findall(json_pattern, raw_output, re.DOTALL)

        if matches:
            # Return the largest match (likely the complete JSON)
            largest = max(matches, key=len)
            self.logger.debug("Found raw JSON in output")
            return largest

        # If nothing found, assume entire output is JSON
        self.logger.debug("No JSON markers found, treating entire output as JSON")
        return raw_output.strip()

    def parse_json(self, raw_output: str) -> dict[str, Any] | list[Any]:
        """
        Parse raw output as JSON.

        Args:
            raw_output: Raw output from Copilot CLI

        Returns:
            Parsed JSON as dict or list

        Raises:
            OutputParseError: If output cannot be parsed as JSON
        """
        try:
            json_str = self.extract_json(raw_output)
            parsed = json.loads(json_str)
            self.logger.debug("Successfully parsed JSON output")
            return parsed

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            self.logger.log_raw_output("parse_error", raw_output, is_error=True)
            raise OutputParseError(
                f"Failed to parse output as JSON: {e}",
                raw_output=raw_output,
            ) from e

    def validate_schema(
        self,
        data: dict[str, Any] | list[Any],
        schema: type[T],
    ) -> T:
        """
        Validate parsed data against a Pydantic schema.

        Args:
            data: Parsed JSON data
            schema: Pydantic model class to validate against

        Returns:
            Validated Pydantic model instance

        Raises:
            SchemaValidationError: If data doesn't match schema
        """
        try:
            validated = schema.model_validate(data)
            self.logger.debug(f"Successfully validated against {schema.__name__}")
            return validated

        except ValidationError as e:
            self.logger.error(f"Schema validation failed: {e}")
            errors = e.errors()
            raise SchemaValidationError(
                f"Output doesn't match expected schema {schema.__name__}",
                validation_errors=errors,
            ) from e

    def parse_and_validate(
        self,
        raw_output: str,
        schema: type[T],
    ) -> T:
        """
        Parse raw output and validate against schema in one step.

        Args:
            raw_output: Raw output from Copilot CLI
            schema: Pydantic model class to validate against

        Returns:
            Validated Pydantic model instance

        Raises:
            OutputParseError: If parsing fails
            SchemaValidationError: If validation fails
        """
        parsed_data = self.parse_json(raw_output)
        return self.validate_schema(parsed_data, schema)

    def try_parse_and_validate(
        self,
        raw_output: str,
        schema: type[T],
    ) -> T | None:
        """
        Attempt to parse and validate, returning None on failure instead of raising.

        Args:
            raw_output: Raw output from Copilot CLI
            schema: Pydantic model class to validate against

        Returns:
            Validated model instance or None if parsing/validation fails
        """
        try:
            return self.parse_and_validate(raw_output, schema)
        except (OutputParseError, SchemaValidationError) as e:
            self.logger.warning(f"Parse/validation failed: {e}")
            return None
