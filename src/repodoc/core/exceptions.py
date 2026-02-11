"""Custom exceptions for RepoDoctor."""

from typing import Any


class RepoDocError(Exception):
    """Base exception for all RepoDoctor errors."""

    def __init__(self, message: str, hint: str | None = None) -> None:
        """
        Initialize error with message and optional hint.

        Args:
            message: Error message
            hint: Optional hint for resolving the error
        """
        self.hint = hint
        full_message = message
        if hint:
            full_message = f"{message}\n\n💡 Hint: {hint}"
        super().__init__(full_message)


class CopilotNotFoundError(RepoDocError):
    """Raised when Copilot CLI is not installed or not found in PATH."""

    def __init__(self) -> None:
        message = (
            "GitHub Copilot CLI not found in your PATH.\n\n"
            "RepoDoctor requires the GitHub Copilot CLI to function."
        )
        hint = (
            "Install GitHub Copilot CLI with:\n"
            "  npm install -g @github/copilot\n\n"
            "Launch Copilot CLI:\n"
            "  copilot\n\n"
            "Then authenticate:\n"
            "  /login\n\n"
            "More info: https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli"
        )
        super().__init__(message, hint)


class CopilotExecutionError(RepoDocError):
    """Raised when Copilot CLI execution fails."""

    def __init__(
        self, message: str, stderr: str | None = None, exit_code: int | None = None
    ) -> None:
        self.stderr = stderr
        self.exit_code = exit_code

        hint = None
        if exit_code == 1 and stderr and "authentication" in stderr.lower():
            hint = "Run 'copilot' and then '/login' to authenticate with GitHub Copilot"
        elif stderr:
            hint = f"Copilot CLI error output:\n{stderr[:200]}"

        super().__init__(message, hint)


class CopilotTimeoutError(RepoDocError):
    """Raised when Copilot CLI execution times out."""

    def __init__(self, timeout: int | None) -> None:
        timeout_str = f"{timeout}" if timeout is not None else "default"
        message = f"Copilot CLI execution timed out after {timeout_str} seconds"
        hint = (
            "Try increasing the timeout with a larger value, or check if your "
            "repository is very large. Large repositories may take longer to analyze."
        )
        super().__init__(message, hint)


class OutputParseError(RepoDocError):
    """Raised when output cannot be parsed as valid JSON."""

    def __init__(self, message: str, raw_output: str) -> None:
        self.raw_output = raw_output
        hint = (
            "The Copilot CLI response was not valid JSON. "
            "This might be a temporary issue. Try running the command again. "
            "Raw output has been logged for debugging."
        )
        super().__init__(message, hint)


class SchemaValidationError(RepoDocError):
    """Raised when output doesn't match expected Pydantic schema."""

    def __init__(self, message: str, validation_errors: list[Any]) -> None:
        self.validation_errors = validation_errors
        error_summary = self._format_validation_errors(validation_errors)
        hint = (
            f"The Copilot CLI returned data that doesn't match the expected "
            f"format:\n{error_summary}\n\n"
            "This might indicate a change in Copilot's output format. "
            "Please report this issue with the full error details."
        )
        super().__init__(message, hint)

    @staticmethod
    def _format_validation_errors(errors: list[Any]) -> str:
        """Format validation errors for display."""
        formatted = []
        for err in errors[:3]:  # Show first 3 errors
            if isinstance(err, dict):
                loc = " -> ".join(str(x) for x in err.get("loc", []))
                msg = err.get("msg", "Unknown error")
                formatted.append(f"  • {loc}: {msg}")
            else:
                formatted.append(f"  • {err}")

        if len(errors) > 3:
            formatted.append(f"  ... and {len(errors) - 3} more errors")

        return "\n".join(formatted)


class EmptyRepositoryError(RepoDocError):
    """Raised when repository is empty or has no analyzable content."""

    def __init__(self) -> None:
        message = "Repository appears to be empty or has no analyzable content"
        hint = "Make sure you're in a directory with source code files"
        super().__init__(message, hint)


class InvalidRepositoryError(RepoDocError):
    """Raised when current directory is not a valid repository."""

    def __init__(self, path: str) -> None:
        message = f"Not a valid repository directory: {path}"
        hint = "Run this command from within a code repository directory"
        super().__init__(message, hint)
