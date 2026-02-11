"""Prompt template loading and management."""

from pathlib import Path
from typing import Any

from repodoc.core.logger import get_logger


class PromptTemplate:
    """Represents a versioned prompt template."""

    def __init__(self, command: str, version: str, content: str) -> None:
        self.command = command
        self.version = version
        self.content = content

    def render(self, **variables: Any) -> str:
        """
        Render the template with variables.

        Args:
            **variables: Variables to substitute in the template

        Returns:
            Rendered prompt string
        """
        # Simple variable substitution for now
        # Can be extended to use Jinja2 or similar if needed
        rendered = self.content
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered


class PromptLoader:
    """Loads and manages prompt templates."""

    def __init__(self, prompts_dir: Path | None = None, version: str = "v1") -> None:
        """
        Initialize prompt loader.

        Args:
            prompts_dir: Directory containing prompt templates (defaults to package prompts/)
            version: Version of prompts to load (default: v1)
        """
        if prompts_dir is None:
            # Default to package prompts directory
            prompts_dir = Path(__file__).parent / version
        elif not (prompts_dir / version).exists():
            prompts_dir = prompts_dir / version

        self.prompts_dir = prompts_dir
        self.version = version
        self.logger = get_logger()
        self._templates: dict[str, PromptTemplate] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all prompt templates from the prompts directory."""
        if not self.prompts_dir.exists():
            self.logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return

        for template_file in self.prompts_dir.glob("*.txt"):
            command_name = template_file.stem
            try:
                content = template_file.read_text(encoding="utf-8")
                self._templates[command_name] = PromptTemplate(
                    command=command_name, version=self.version, content=content
                )
                self.logger.debug(
                    f"Loaded prompt template: {command_name} (version: {self.version})"
                )
            except Exception as e:
                self.logger.error(f"Failed to load template {template_file}: {e}")

        self.logger.info(f"Loaded {len(self._templates)} prompt templates")

    def get_template(self, command: str) -> PromptTemplate:
        """
        Get a prompt template by command name.

        Args:
            command: Command name (e.g., 'diet', 'tour', 'docker')

        Returns:
            PromptTemplate instance

        Raises:
            KeyError: If template not found
        """
        if command not in self._templates:
            available = ", ".join(self._templates.keys())
            raise KeyError(f"Prompt template '{command}' not found. Available: {available}")
        return self._templates[command]

    def get_prompt(self, command: str, **variables: Any) -> str:
        """
        Get rendered prompt for a command.

        Args:
            command: Command name
            **variables: Variables to substitute in template

        Returns:
            Rendered prompt string
        """
        template = self.get_template(command)
        return template.render(**variables)

    def list_commands(self) -> list[str]:
        """List all available command templates."""
        return list(self._templates.keys())


# Global prompt loader instance
_loader: PromptLoader | None = None


def get_prompt_loader(version: str = "v1") -> PromptLoader:
    """
    Get or create the global prompt loader instance.

    Args:
        version: Prompt version to load (default: v1)

    Returns:
        PromptLoader instance
    """
    global _loader
    if _loader is None or _loader.version != version:
        _loader = PromptLoader(version=version)
    return _loader
