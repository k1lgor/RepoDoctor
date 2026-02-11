"""Logging utilities for RepoDoctor."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any


class RepoDocLogger:
    """Centralized logging system for RepoDoctor."""

    def __init__(self, log_dir: Path | None = None) -> None:
        """Initialize logger with optional custom log directory."""
        if log_dir is None:
            log_dir = Path.cwd() / ".repodoc" / "logs"

        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger("repodoc")
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            # File handler for all logs
            log_file = self.log_dir / f"repodoc_{datetime.now():%Y%m%d_%H%M%S}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)

            # Console handler - only CRITICAL messages (effectively disabled for normal errors)
            # Users get clean error messages from Rich console, not logger output
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.CRITICAL)

            # Formatter
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        exc_info = kwargs.pop("exc_info", None)
        self.logger.debug(message, exc_info=exc_info, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        exc_info = kwargs.pop("exc_info", None)
        self.logger.info(message, exc_info=exc_info, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        exc_info = kwargs.pop("exc_info", None)
        self.logger.warning(message, exc_info=exc_info, extra=kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        exc_info = kwargs.pop("exc_info", None)
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def log_raw_output(self, command: str, output: str, is_error: bool = False) -> Path:
        """Log raw output from Copilot CLI to a separate file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        prefix = "error" if is_error else "output"
        output_file = self.log_dir / f"{prefix}_{command}_{timestamp}.txt"

        output_file.write_text(output, encoding="utf-8")
        self.info(f"Raw output saved to {output_file}")
        return output_file


# Global logger instance
_logger: RepoDocLogger | None = None


def get_logger() -> RepoDocLogger:
    """Get or create the global logger instance."""
    global _logger
    if _logger is None:
        _logger = RepoDocLogger()
    return _logger
