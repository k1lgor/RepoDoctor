"""Unit tests for exception classes."""

import pytest

from repodoc.core.exceptions import (
    CopilotExecutionError,
    CopilotNotFoundError,
    CopilotTimeoutError,
    EmptyRepositoryError,
    InvalidRepositoryError,
    OutputParseError,
    RepoDocError,
    SchemaValidationError,
)


@pytest.mark.unit
class TestExceptions:
    """Tests for custom exception classes."""

    def test_repodoc_error_base(self) -> None:
        """Test base RepoDocError with message and hint."""
        error = RepoDocError("Something went wrong", hint="Try this fix")

        assert "Something went wrong" in str(error)
        assert "Try this fix" in str(error)
        assert "💡 Hint:" in str(error)

    def test_repodoc_error_without_hint(self) -> None:
        """Test RepoDocError without hint."""
        error = RepoDocError("Something went wrong")

        assert "Something went wrong" in str(error)
        assert "Hint" not in str(error)

    def test_copilot_not_found_error(self) -> None:
        """Test CopilotNotFoundError message."""
        error = CopilotNotFoundError()

        message = str(error)
        assert "not found" in message.lower()
        assert "install" in message.lower()
        assert "npm install" in message

    def test_copilot_execution_error_basic(self) -> None:
        """Test CopilotExecutionError with basic message."""
        error = CopilotExecutionError("Command failed")

        assert "Command failed" in str(error)

    def test_copilot_execution_error_with_stderr(self) -> None:
        """Test CopilotExecutionError with stderr."""
        error = CopilotExecutionError("Command failed", stderr="Error details")

        assert error.stderr == "Error details"

    def test_copilot_execution_error_auth_hint(self) -> None:
        """Test CopilotExecutionError provides auth hint."""
        error = CopilotExecutionError("Command failed", stderr="authentication failed", exit_code=1)

        message = str(error)
        assert "auth" in message.lower()

    def test_copilot_timeout_error(self) -> None:
        """Test CopilotTimeoutError message."""
        error = CopilotTimeoutError(timeout=120)

        message = str(error)
        assert "120 seconds" in message
        assert "timeout" in message.lower()

    def test_output_parse_error(self) -> None:
        """Test OutputParseError stores raw output."""
        raw = "Invalid JSON output"
        error = OutputParseError("Failed to parse", raw_output=raw)

        assert error.raw_output == raw
        assert "Failed to parse" in str(error)

    def test_schema_validation_error(self) -> None:
        """Test SchemaValidationError formats errors."""
        validation_errors = [
            {"loc": ("field1",), "msg": "Field required"},
            {"loc": ("nested", "field2"), "msg": "Invalid type"},
        ]

        error = SchemaValidationError("Validation failed", validation_errors)

        assert error.validation_errors == validation_errors
        message = str(error)
        assert "field1" in message
        assert "field2" in message

    def test_schema_validation_error_many_errors(self) -> None:
        """Test SchemaValidationError limits displayed errors."""
        validation_errors = [{"loc": (f"field{i}",), "msg": f"Error {i}"} for i in range(10)]

        error = SchemaValidationError("Validation failed", validation_errors)

        message = str(error)
        # Should show first 3 and count
        assert "field0" in message
        assert "field1" in message
        assert "field2" in message
        assert "7 more errors" in message

    def test_empty_repository_error(self) -> None:
        """Test EmptyRepositoryError message."""
        error = EmptyRepositoryError()

        message = str(error)
        assert "empty" in message.lower()
        assert "analyzable content" in message.lower()

    def test_invalid_repository_error(self) -> None:
        """Test InvalidRepositoryError message."""
        error = InvalidRepositoryError("/path/to/repo")

        message = str(error)
        assert "/path/to/repo" in message
        assert "not a valid repository" in message.lower()

    def test_all_errors_inherit_from_repodoc_error(self) -> None:
        """Test all custom errors inherit from RepoDocError."""
        errors = [
            CopilotNotFoundError(),
            CopilotExecutionError("test"),
            CopilotTimeoutError(120),
            OutputParseError("test", "raw"),
            SchemaValidationError("test", []),
            EmptyRepositoryError(),
            InvalidRepositoryError("/test"),
        ]

        for error in errors:
            assert isinstance(error, RepoDocError)
            assert isinstance(error, Exception)
