"""Unit tests for CopilotInvoker class."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from repodoc.core.copilot import CopilotInvoker
from repodoc.core.exceptions import (
    CopilotExecutionError,
    CopilotTimeoutError,
)


@pytest.mark.unit
class TestCopilotInvoker:
    """Tests for CopilotInvoker class."""

    def test_initialization(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test CopilotInvoker initializes with no default timeout."""
        import shutil

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        invoker = CopilotInvoker()
        assert invoker.timeout is None

    def test_initialization_custom_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test CopilotInvoker initializes with custom timeout."""
        import shutil

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        invoker = CopilotInvoker(timeout=300)
        assert invoker.timeout == 300

    def test_validate_copilot_checks_availability(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Copilot CLI validation happens during initialization."""
        import shutil

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        def mock_run(*args: tuple, **kwargs: dict) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Should not raise during initialization
        invoker = CopilotInvoker()
        assert invoker.timeout is None

    def test_invoke_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test successful Copilot CLI invocation."""
        import shutil

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        expected_output = json.dumps({"result": "success"})

        def mock_run(*args: tuple, **kwargs: dict) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            result.stdout = expected_output
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        invoker = CopilotInvoker()
        output = invoker.invoke("Test prompt")

        assert output == expected_output

    @pytest.mark.skip(reason="Requires GitHub Copilot CLI to be installed")
    def test_invoke_with_cwd(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Test Copilot CLI invocation with custom working directory."""
        captured_cwd = None

        def mock_run(*args: tuple, **kwargs: dict) -> MagicMock:
            nonlocal captured_cwd
            captured_cwd = kwargs.get("cwd")
            result = MagicMock()
            result.returncode = 0
            result.stdout = "{}"
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        invoker = CopilotInvoker()
        invoker.invoke("Test prompt", cwd=tmp_path)

        assert captured_cwd == tmp_path

    def test_invoke_timeout(self, mock_copilot_timeout: None) -> None:
        """Test Copilot CLI invocation timeout."""
        invoker = CopilotInvoker(timeout=1)

        with pytest.raises(CopilotTimeoutError) as exc_info:
            invoker.invoke("Test prompt")

        assert "timed out after 1 seconds" in str(exc_info.value)

    @pytest.mark.skip(reason="Requires GitHub Copilot CLI to be installed")
    def test_invoke_execution_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Copilot CLI execution error."""

        def mock_run(*args: tuple, **kwargs: dict) -> MagicMock:
            result = MagicMock()
            result.returncode = 1
            result.stdout = ""
            result.stderr = "Authentication failed"
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        invoker = CopilotInvoker()

        with pytest.raises(CopilotExecutionError) as exc_info:
            invoker.invoke("Test prompt")

        assert "authentication" in str(exc_info.value).lower()

    @pytest.mark.skip(reason="Requires GitHub Copilot CLI to be installed")
    def test_invoke_empty_output(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Copilot CLI returns empty output."""

        def mock_run(*args: tuple, **kwargs: dict) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        invoker = CopilotInvoker()

        with pytest.raises(CopilotExecutionError) as exc_info:
            invoker.invoke("Test prompt")

        assert "no output" in str(exc_info.value).lower()

    @pytest.mark.skip(reason="Requires GitHub Copilot CLI to be installed")
    def test_invoke_with_retry_success_first_try(
        self, monkeypatch: pytest.MonkeyPatch, sample_diet_response: dict
    ) -> None:
        """Test invoke_with_retry succeeds on first attempt."""

        def mock_run(*args: tuple, **kwargs: dict) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            result.stdout = json.dumps(sample_diet_response)
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        invoker = CopilotInvoker()
        output, was_retried = invoker.invoke_with_retry("Test prompt")

        assert was_retried is False  # Should succeed first try
        assert json.loads(output) == sample_diet_response

    @pytest.mark.skip(reason="Requires GitHub Copilot CLI to be installed")
    def test_invoke_with_retry_success_second_try(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test invoke_with_retry succeeds on retry after execution error."""
        call_count = 0

        def mock_run(*args: tuple, **kwargs: dict) -> MagicMock:
            nonlocal call_count
            call_count += 1
            result = MagicMock()

            if call_count == 1:
                # First call fails with execution error
                result.returncode = 1
                result.stderr = "Temporary error"
            else:
                # Second call succeeds
                result.returncode = 0
                result.stdout = json.dumps({"result": "success"})
                result.stderr = ""

            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        invoker = CopilotInvoker()
        output, was_retried = invoker.invoke_with_retry("Test prompt")

        assert call_count == 2  # Should retry once
        assert was_retried is True  # Was retried

    @pytest.mark.skip(reason="Requires GitHub Copilot CLI to be installed")
    def test_invoke_with_retry_both_fail(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test invoke_with_retry fails both attempts."""

        def mock_run(*args: tuple, **kwargs: dict) -> MagicMock:
            result = MagicMock()
            result.returncode = 1
            result.stderr = "Persistent error"
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        invoker = CopilotInvoker()

        with pytest.raises(CopilotExecutionError):
            invoker.invoke_with_retry("Test prompt")
