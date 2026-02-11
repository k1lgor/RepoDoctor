"""JSON output renderer."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from repodoc.renderers.base import BaseRenderer


class JSONRenderer(BaseRenderer):
    """Renders output as formatted JSON."""

    def __init__(self, verbose: bool = False, indent: int = 2) -> None:
        """
        Initialize JSON renderer.

        Args:
            verbose: Enable verbose output
            indent: JSON indentation level
        """
        super().__init__(verbose)
        self.indent = indent

    def render(self, data: BaseModel | dict[str, Any]) -> str:
        """
        Render data as JSON string.

        Args:
            data: Data to render

        Returns:
            JSON formatted string
        """
        data_dict = self._to_dict(data)
        return json.dumps(data_dict, indent=self.indent, ensure_ascii=False)

    def render_to_file(self, data: BaseModel | dict[str, Any], output_path: Path) -> None:
        """
        Render data and write to JSON file.

        Args:
            data: Data to render
            output_path: Path to JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            data_dict = self._to_dict(data)
            json.dump(data_dict, f, indent=self.indent, ensure_ascii=False)
