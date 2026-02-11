"""Base command infrastructure with common patterns and utilities."""

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from repodoc.core.exceptions import RepoDocError
from repodoc.core.logger import get_logger

# Force UTF-8 for Rich console output
console = Console(force_terminal=None, legacy_windows=False)
logger = get_logger()


def get_repo_root() -> Path:
    """
    Get the repository root directory (current working directory).

    Returns:
        Path to repository root

    Raises:
        EmptyRepositoryError: If repository has no analyzable content
    """
    from repodoc.core.exceptions import EmptyRepositoryError

    cwd = Path.cwd().resolve()
    logger.debug(f"Working directory: {cwd}")

    # Basic validation: check if directory has any code files
    has_content = False
    common_code_extensions = {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".go",
        ".rs",
        ".rb",
        ".cpp",
        ".c",
        ".h",
        ".css",
        ".html",
    }

    try:
        # Quick check: look for at least one code file in first few levels
        for item in cwd.iterdir():
            if item.is_file() and item.suffix in common_code_extensions:
                has_content = True
                break
            elif item.is_dir() and not item.name.startswith("."):
                # Check one level deep
                for subitem in item.iterdir():
                    if subitem.is_file() and subitem.suffix in common_code_extensions:
                        has_content = True
                        break
            if has_content:
                break
    except (PermissionError, OSError):
        # If we can't read, assume it's okay
        logger.warning("Could not fully validate repository content")
        return cwd

    if not has_content:
        logger.warning(f"No code files found in {cwd}")
        raise EmptyRepositoryError()

    return cwd


def ensure_repodoc_dir(repo_root: Path) -> Path:
    """Ensure .repodoc directory exists in repository root."""
    repodoc_dir = repo_root / ".repodoc"
    repodoc_dir.mkdir(exist_ok=True)
    logger.debug(f"Ensured .repodoc directory: {repodoc_dir}")
    return repodoc_dir


def save_json_output(data: Any, output_path: Path) -> None:
    """Save structured data as JSON to specified path."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"[green]✓[/green] JSON output saved to: {output_path}")
        logger.info(f"Saved JSON output to {output_path}")
    except Exception as e:
        error_msg = f"Failed to save JSON output to {output_path}: {e}"
        logger.error(error_msg)
        raise RepoDocError(error_msg) from e


def save_text_output(output_path: Path, render_func, *args, **kwargs) -> None:
    """
    Save formatted text output to file by capturing rendered content.

    Args:
        output_path: Path to save the output
        render_func: Renderer function to call (e.g., renderer.render)
        *args, **kwargs: Arguments to pass to the render function
    """
    try:
        from rich.console import Console

        # Create a file console that writes to the output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            file_console = Console(
                file=f,
                width=120,
                force_terminal=False,  # Disable color codes for file
                legacy_windows=False,
            )

            # Create a new terminal renderer with the file console
            from repodoc.renderers.terminal_renderer import TerminalRenderer

            file_terminal = TerminalRenderer(
                verbose=kwargs.get("verbose", False), console=file_console
            )

            # Replace the console in the renderer temporarily
            original_terminal = kwargs.get("terminal")
            if original_terminal:
                # Create new renderer with file terminal
                renderer_class = render_func.__self__.__class__
                file_renderer = renderer_class(file_terminal)
                # Call render method with file renderer
                getattr(file_renderer, render_func.__name__)(*args)

        console.print(f"[green]✓[/green] Output saved to: {output_path}")
        logger.info(f"Saved text output to {output_path}")
    except Exception as e:
        error_msg = f"Failed to save output to {output_path}: {e}"
        logger.error(error_msg)
        raise RepoDocError(error_msg) from e


def handle_json_flag(data: dict[str, Any], json_flag: bool, out_path: str | None) -> None:
    """Handle --json and --out flags for structured output."""
    if json_flag and not out_path:
        # Use print() for pure JSON output without Rich formatting
        print(json.dumps(data, indent=2))
    elif out_path:
        output_file = Path(out_path)
        save_json_output(data, output_file)


def print_success_message(command: str, next_actions: list[str] | None = None) -> None:
    """
    Print a success message with optional next actions.

    Args:
        command: Name of the command that succeeded
        next_actions: List of suggested next actions
    """
    console.print(f"\n[green bold]✓ {command} completed successfully![/green bold]")

    if next_actions:
        console.print("\n[cyan]💡 Next steps:[/cyan]")
        for action in next_actions:
            console.print(f"  • {action}")


def print_progress(message: str, emoji: str = "⏳") -> None:
    """Print a progress message with emoji."""
    console.print(f"\n{emoji} {message}...")


def render_health_score(score: float, label: str = "Health Score") -> None:
    """Render a health score with color coding."""
    if score >= 80:
        color = "green"
        emoji = "✓"
    elif score >= 60:
        color = "yellow"
        emoji = "⚠"
    else:
        color = "red"
        emoji = "✗"

    console.print(
        Panel(f"[{color} bold]{emoji} {label}: {score}/100[/{color} bold]", border_style=color)
    )


def render_issues_table(issues: list[dict[str, Any]], title: str = "Issues") -> None:
    """Render a table of issues with severity indicators."""
    if not issues:
        console.print(f"[green]✓[/green] No {title.lower()} found")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Severity", style="dim", width=10)
    table.add_column("Category", style="cyan", width=15)
    table.add_column("Description")

    for issue in issues:
        severity = issue.get("severity", "unknown")
        category = issue.get("category", "general")
        description = issue.get("description", "")

        severity_color = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "blue",
            "info": "dim",
        }.get(severity, "white")

        table.add_row(
            f"[{severity_color}]{severity.upper()}[/{severity_color}]", category, description
        )

    console.print(table)


def render_recommendations(recommendations: list[dict[str, Any]]) -> None:
    """Render recommendations as a formatted list."""
    if not recommendations:
        return

    console.print("\n[bold cyan]Recommendations:[/bold cyan]")
    for i, rec in enumerate(recommendations, 1):
        title = rec.get("title", "Recommendation")
        description = rec.get("description", "")
        console.print(f"  {i}. [yellow]{title}[/yellow]")
        console.print(f"     {description}\n")


def handle_command_error(error: Exception, verbose: bool = False) -> None:
    """Handle command errors with appropriate logging and user messages."""
    from repodoc.core.exceptions import (
        CopilotExecutionError,
        CopilotNotFoundError,
        CopilotTimeoutError,
        EmptyRepositoryError,
        InvalidRepositoryError,
        OutputParseError,
        RepoDocError,
        SchemaValidationError,
    )

    error_msg = str(error)
    logger.error(f"Command failed: {error_msg}", exc_info=verbose)

    # Handle specific error types with tailored messages
    if isinstance(error, CopilotNotFoundError):
        console.print("[red bold]✗ Copilot CLI Not Found[/red bold]")
        console.print(error_msg)
    elif isinstance(error, CopilotTimeoutError):
        console.print("[red bold]✗ Operation Timed Out[/red bold]")
        console.print(error_msg)
    elif isinstance(error, CopilotExecutionError):
        console.print("[red bold]✗ Copilot Execution Failed[/red bold]")
        console.print(error_msg)
    elif isinstance(error, (OutputParseError, SchemaValidationError)):
        console.print("[red bold]✗ Output Parsing Failed[/red bold]")
        console.print(error_msg)
        if verbose:
            console.print("\n[dim]Enable --verbose for more details[/dim]")
    elif isinstance(error, (EmptyRepositoryError, InvalidRepositoryError)):
        console.print("[red bold]✗ Repository Error[/red bold]")
        console.print(error_msg)
    elif isinstance(error, RepoDocError):
        console.print(f"[red]✗ Error:[/red] {error_msg}")
    else:
        console.print(f"[red]✗ Unexpected error:[/red] {error_msg}")
        if verbose:
            console.print_exception()
        else:
            console.print("\n[dim]Run with --verbose for full error details[/dim]")

    raise typer.Exit(code=1)
