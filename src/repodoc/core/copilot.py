"""Copilot CLI invocation module."""

import shutil
import subprocess
from pathlib import Path

from repodoc.core.exceptions import (
    CopilotExecutionError,
    CopilotNotFoundError,
    CopilotTimeoutError,
)
from repodoc.core.logger import get_logger


class CopilotInvoker:
    """Handles invocation of GitHub Copilot CLI."""

    def __init__(self, timeout: int | None = None) -> None:
        """
        Initialize Copilot invoker.

        Args:
            timeout: Maximum time in seconds to wait for Copilot CLI response (optional, no default)
        """
        self.timeout = timeout
        self.logger = get_logger()
        self._validate_copilot_available()

    def _validate_copilot_available(self) -> None:
        """Check if Copilot CLI is available in PATH."""
        if shutil.which("copilot") is None:
            self.logger.error("Copilot CLI not found in PATH")
            raise CopilotNotFoundError()
        self.logger.debug("Copilot CLI found in PATH")

    def invoke(
        self,
        prompt: str,
        cwd: Path | None = None,
        timeout: int | None = None,
    ) -> str:
        """
        Invoke Copilot CLI with a prompt.

        Args:
            prompt: The prompt to send to Copilot CLI
            cwd: Working directory for the command (defaults to current directory)
            timeout: Override default timeout for this invocation

        Returns:
            Raw output from Copilot CLI

        Raises:
            CopilotExecutionError: If Copilot CLI execution fails
            CopilotTimeoutError: If execution times out
        """
        if cwd is None:
            cwd = Path.cwd()

        if timeout is None:
            timeout = self.timeout

        command = ["copilot", "-p", prompt]

        self.logger.info(f"Invoking Copilot CLI in {cwd}")
        self.logger.debug(f"Command: {' '.join(command)}")
        self.logger.debug(f"Prompt: {prompt[:200]}...")  # Log first 200 chars

        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding='utf-8',  # Force UTF-8 encoding to handle all characters
                errors='replace',  # Replace invalid characters instead of crashing
                timeout=timeout,
                check=False,
            )

            if result.returncode != 0:
                stderr = result.stderr.strip() if result.stderr else ""
                self.logger.error(f"Copilot CLI failed with exit code {result.returncode}")
                self.logger.log_raw_output("copilot_error", stderr, is_error=True)

                # Provide helpful error messages based on stderr
                error_msg = "Copilot CLI execution failed"
                if "authentication" in stderr.lower() or "auth" in stderr.lower():
                    error_msg = (
                        "Copilot CLI authentication failed. "
                        "Run 'copilot' to launch Copilot CLI."
                        "Then /login to authenticate."
                    )
                elif "not found" in stderr.lower():
                    error_msg = "Copilot CLI command not recognized"
                elif stderr:
                    error_msg = f"Copilot CLI error: {stderr[:200]}"

                raise CopilotExecutionError(error_msg, stderr, result.returncode)

            output = result.stdout.strip() if result.stdout else ""

            # Check for empty output
            if not output:
                self.logger.warning("Copilot CLI returned empty output")
                raise CopilotExecutionError(
                    "Copilot CLI returned no output. Repository might be too small or empty.",
                    stderr=result.stderr if result.stderr else "",
                    exit_code=result.returncode,
                )

            self.logger.debug("Copilot CLI completed successfully")
            self.logger.log_raw_output("copilot_output", output)

            return output

        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Copilot CLI timed out after {timeout} seconds")
            raise CopilotTimeoutError(timeout) from e

        except FileNotFoundError as e:
            # This shouldn't happen due to validation, but handle it anyway
            self.logger.error("Copilot CLI executable not found")
            raise CopilotNotFoundError() from e

    def invoke_with_retry(
        self,
        prompt: str,
        cwd: Path | None = None,
        timeout: int | None = None,
        retry_prompt_suffix: str | None = None,
    ) -> tuple[str, bool]:
        """
        Invoke Copilot CLI with automatic retry on failure.

        Args:
            prompt: The prompt to send to Copilot CLI
            cwd: Working directory for the command
            timeout: Override default timeout
            retry_prompt_suffix: Additional text to append to prompt on retry

        Returns:
            Tuple of (output, was_retried)

        Raises:
            CopilotExecutionError: If both attempts fail
            CopilotTimeoutError: If execution times out
        """
        if retry_prompt_suffix is None:
            retry_prompt_suffix = (
                "\n\nIMPORTANT: Format your response as strict JSON only. "
                "No markdown code blocks, no explanatory text."
            )

        try:
            output = self.invoke(prompt, cwd, timeout)
            return (output, False)

        except CopilotExecutionError as e:
            self.logger.warning("First attempt failed, retrying with strict formatting...")
            retry_prompt = prompt + retry_prompt_suffix

            try:
                output = self.invoke(retry_prompt, cwd, timeout)
                self.logger.info("Retry successful")
                return (output, True)

            except CopilotExecutionError as retry_error:
                self.logger.error("Both attempts failed")
                raise retry_error from e
