"""Output rendering system for RepoDoctor CLI."""

from repodoc.renderers.base import BaseRenderer, OutputFormat
from repodoc.renderers.json_renderer import JSONRenderer
from repodoc.renderers.terminal_renderer import TerminalRenderer

__all__ = ["BaseRenderer", "OutputFormat", "JSONRenderer", "TerminalRenderer"]
