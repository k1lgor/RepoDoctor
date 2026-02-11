"""CLI entry point for RepoDoctor."""

import contextlib
import locale
import sys

import typer
from rich.console import Console

from repodoc import __version__
from repodoc.commands import deadcode, diet, docker, report, scan, tour

# Force UTF-8 encoding for all output streams (Windows compatibility)
if sys.platform == "win32":
    # Set console code page to UTF-8 on Windows
    with contextlib.suppress(Exception):
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)

# Set default encoding for Python's text streams
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Set locale to UTF-8 if possible
with contextlib.suppress(locale.Error):
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
with contextlib.suppress(locale.Error):
    locale.setlocale(locale.LC_ALL, "C.UTF-8")

app = typer.Typer(
    name="repodoc",
    help="""
    🏥 RepoDoctor - AI-Powered Repository Health Analysis

    RepoDoctor uses GitHub Copilot CLI to analyze your codebase and provide
    actionable insights on repository health, code quality, and best practices.

    📋 Quick Start:

      $ repodoc scan              # Full health check
      $ repodoc diet              # Find bloat and missing files
      $ repodoc tour              # Generate TOUR.md for onboarding
      $ repodoc docker            # Analyze Dockerfiles
      $ repodoc deadcode          # Detect unused code

    ⚙️  Requirements:

      • GitHub Copilot CLI must be installed and authenticated
      • Run from within a code repository directory

    📖 For detailed help on each command:

      $ repodoc <command> --help
    """,
    add_completion=False,
    no_args_is_help=True,
)
# Force UTF-8 for Rich console output
console = Console(force_terminal=None, legacy_windows=False)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold]RepoDoctor[/bold] version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """RepoDoctor - Copilot-powered repository health analysis."""
    pass


# Register commands
app.command(name="diet")(diet)
app.command(name="tour")(tour)
app.command(name="docker")(docker)
app.command(name="deadcode")(deadcode)
app.command(name="scan")(scan)
app.command(name="report")(report)


if __name__ == "__main__":
    app()
