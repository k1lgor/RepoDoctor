"""Base renderer classes and interfaces."""

from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class OutputFormat(StrEnum):
    """Supported output formats."""

    TERMINAL = "terminal"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


class BaseRenderer(ABC):
    """Abstract base class for all output renderers."""

    def __init__(self, verbose: bool = False) -> None:
        """
        Initialize renderer.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose

    @abstractmethod
    def render(self, data: BaseModel | dict[str, Any]) -> str:
        """
        Render data to output format.

        Args:
            data: Data to render (Pydantic model or dict)

        Returns:
            Formatted output string
        """
        pass

    @abstractmethod
    def render_to_file(self, data: BaseModel | dict[str, Any], output_path: Path) -> None:
        """
        Render data and write to file.

        Args:
            data: Data to render
            output_path: Path to output file
        """
        pass

    def _to_dict(self, data: BaseModel | dict[str, Any]) -> dict[str, Any]:
        """
        Convert data to dictionary format.

        Args:
            data: Pydantic model or dict

        Returns:
            Dictionary representation
        """
        if isinstance(data, BaseModel):
            return data.model_dump()
        return data
