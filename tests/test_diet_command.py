"""Integration tests for diet command."""

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from repodoc.cli import app

runner = CliRunner()


@pytest.mark.integration
class TestDietCommand:
    """Integration tests for diet command."""

    def test_diet_command_success(
        self, monkeypatch: pytest.MonkeyPatch, temp_repo: Path, sample_diet_response: dict[str, Any]
    ) -> None:
        """Test diet command with successful response."""
        # Mock subprocess to return valid diet response
        import shutil
        import subprocess
        from unittest.mock import MagicMock

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            result.stdout = json.dumps(sample_diet_response)
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.chdir(temp_repo)

        result = runner.invoke(app, ["diet"])

        assert result.exit_code == 0
        assert "Diet analysis" in result.stdout or "diet" in result.stdout.lower()

    def test_diet_command_json_output(
        self, monkeypatch: pytest.MonkeyPatch, temp_repo: Path, sample_diet_response: dict[str, Any]
    ) -> None:
        """Test diet command with --json flag."""
        import shutil
        import subprocess
        from unittest.mock import MagicMock

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            result.stdout = json.dumps(sample_diet_response)
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.chdir(temp_repo)

        result = runner.invoke(app, ["diet", "--json"])

        assert result.exit_code == 0
        # Should output valid JSON (analysis section only)
        output_data = json.loads(result.stdout)
        assert "total_size_bytes" in output_data

    def test_diet_command_output_to_file(
        self, monkeypatch: pytest.MonkeyPatch, temp_repo: Path, sample_diet_response: dict[str, Any]
    ) -> None:
        """Test diet command with --out flag."""
        import shutil
        import subprocess
        from unittest.mock import MagicMock

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            result.stdout = json.dumps(sample_diet_response)
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.chdir(temp_repo)

        output_file = temp_repo / "diet_output.txt"
        result = runner.invoke(app, ["diet", "--out", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify file contains formatted text output
        with open(output_file, encoding="utf-8") as f:
            content = f.read()
        assert "Diet Analysis Results" in content or "Total Size" in content

    def test_diet_command_copilot_not_found(
        self, monkeypatch: pytest.MonkeyPatch, temp_repo: Path
    ) -> None:
        """Test diet command when Copilot CLI is not found."""
        import shutil

        # Mock copilot NOT being available
        monkeypatch.setattr(shutil, "which", lambda cmd: None)
        monkeypatch.chdir(temp_repo)

        result = runner.invoke(app, ["diet"])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower() or "not found" in str(result.exception).lower()

    def test_diet_command_empty_repo(
        self,
        monkeypatch: pytest.MonkeyPatch,
        empty_repo: Path,
        sample_diet_response: dict[str, Any],
    ) -> None:
        """Test diet command on empty repository."""
        import shutil
        import subprocess
        from unittest.mock import MagicMock

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            result.stdout = json.dumps(sample_diet_response)
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.chdir(empty_repo)

        result = runner.invoke(app, ["diet"])

        # Should fail due to empty repo
        assert result.exit_code == 1
        assert "empty" in result.stdout.lower() or "empty" in str(result.exception).lower()

    def test_diet_command_verbose_mode(
        self, monkeypatch: pytest.MonkeyPatch, temp_repo: Path, sample_diet_response: dict[str, Any]
    ) -> None:
        """Test diet command with --verbose flag."""
        import shutil
        import subprocess
        from unittest.mock import MagicMock

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
            result = MagicMock()
            result.returncode = 0
            result.stdout = json.dumps(sample_diet_response)
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.chdir(temp_repo)

        result = runner.invoke(app, ["diet", "--verbose"])

        assert result.exit_code == 0

    @pytest.mark.xfail(reason="Logger exc_info conflict with Typer test runner - known issue")
    def test_diet_command_invalid_json_retry(
        self, monkeypatch: pytest.MonkeyPatch, temp_repo: Path, sample_diet_response: dict[str, Any]
    ) -> None:
        """Test diet command retries on invalid JSON."""
        import shutil
        import subprocess
        from unittest.mock import MagicMock

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        call_count = 0

        def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            result.returncode = 0

            if call_count == 1:
                # First call returns invalid JSON
                result.stdout = "Invalid JSON response"
            else:
                # Retry returns valid JSON
                result.stdout = json.dumps(sample_diet_response)

            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.chdir(temp_repo)

        result = runner.invoke(app, ["diet"])

        # Should succeed after retry
        assert result.exit_code == 0
        assert call_count == 2

    def test_diet_command_custom_timeout(
        self, monkeypatch: pytest.MonkeyPatch, temp_repo: Path, sample_diet_response: dict[str, Any]
    ) -> None:
        """Test diet command with custom timeout."""
        import shutil
        import subprocess
        from unittest.mock import MagicMock

        # Mock copilot being available
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/copilot" if cmd == "copilot" else None
        )

        captured_timeout = None

        def mock_run(*args: Any, **kwargs: Any) -> MagicMock:
            nonlocal captured_timeout
            captured_timeout = kwargs.get("timeout")
            result = MagicMock()
            result.returncode = 0
            result.stdout = json.dumps(sample_diet_response)
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)
        monkeypatch.chdir(temp_repo)

        result = runner.invoke(app, ["diet", "--timeout", "300"])

        assert result.exit_code == 0
        assert captured_timeout == 300
