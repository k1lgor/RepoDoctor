"""Terminal output renderer using Rich library."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from repodoc.renderers.base import BaseRenderer
from repodoc.schemas.base import Issue, Recommendation, RepoHealthScore, Severity


class TerminalRenderer(BaseRenderer):
    """Renders output as formatted terminal display using Rich."""

    def __init__(self, verbose: bool = False, console: Console | None = None) -> None:
        """
        Initialize terminal renderer.

        Args:
            verbose: Enable verbose output
            console: Rich console instance (creates new if None)
        """
        super().__init__(verbose)
        # Force UTF-8 for Rich console output
        self.console = console or Console(force_terminal=None, legacy_windows=False)

    def render(self, data: BaseModel | dict[str, Any]) -> str:
        """
        Render data as terminal output.

        Note: This returns empty string as terminal rendering is done via side effects.
        Use render_* methods for specific components.

        Args:
            data: Data to render

        Returns:
            Empty string (rendering happens via console.print)
        """
        # Terminal rendering is typically done via side effects
        # This method is here for interface compliance
        return ""

    def render_to_file(self, data: BaseModel | dict[str, Any], output_path: Path) -> None:
        """
        Render data to file (exports terminal output).

        Args:
            data: Data to render
            output_path: Path to output file
        """
        # Export console output to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            # Use a console that writes to file
            file_console = Console(file=f, width=120)
            # Re-render to file console (would need specific render methods)
            file_console.print(str(self._to_dict(data)))

    # === Component Renderers ===

    def render_health_score(
        self, score: int | RepoHealthScore, label: str = "Health Score"
    ) -> None:
        """
        Render a health score with color coding.

        Args:
            score: Health score (0-100) or RepoHealthScore object
            label: Label for the score display
        """
        if isinstance(score, RepoHealthScore):
            score_value = score.overall_score
            grade = score.grade
        else:
            score_value = score
            grade = self._calculate_grade(score_value)

        # Color coding based on score
        if score_value >= 80:
            color = "green"
            emoji = "✓"
        elif score_value >= 60:
            color = "yellow"
            emoji = "⚠"
        else:
            color = "red"
            emoji = "✗"

        panel_content = (
            f"[{color} bold]{emoji} {label}: {score_value}/100 (Grade: {grade})[/{color} bold]"
        )
        self.console.print(Panel(panel_content, border_style=color))

    def render_issues_table(
        self, issues: list[Issue] | list[dict[str, Any]], title: str = "Issues"
    ) -> None:
        """
        Render a table of issues with severity indicators.

        Args:
            issues: List of Issue objects or dictionaries
            title: Table title
        """
        if not issues:
            self.console.print(f"[green]✓[/green] No {title.lower()} found")
            return

        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Severity", style="dim", width=10)
        table.add_column("Category", style="cyan", width=15)
        table.add_column("Description", no_wrap=False)
        table.add_column("Location", style="dim", width=20)

        for issue in issues:
            if isinstance(issue, Issue):
                severity = issue.severity
                category = issue.category
                description = issue.description
                location = issue.file_path or "N/A"
            else:
                severity = issue.get("severity", "unknown")
                category = issue.get("category", "general")
                description = issue.get("description", "")
                location = issue.get("file_path") or "N/A"

            severity_color = self._get_severity_color(severity)
            severity_display = f"[{severity_color}]{severity.upper()}[/{severity_color}]"

            table.add_row(severity_display, category, description, location)

        self.console.print(table)

    def render_recommendations(
        self, recommendations: list[Recommendation] | list[dict[str, Any]]
    ) -> None:
        """
        Render recommendations as formatted list.

        Args:
            recommendations: List of Recommendation objects or dictionaries
        """
        if not recommendations:
            return

        self.console.print("\n[bold cyan]Recommendations:[/bold cyan]")
        for i, rec in enumerate(recommendations, 1):
            if isinstance(rec, Recommendation):
                action = rec.action
                reason = rec.reason
                priority = rec.priority
            else:
                action = rec.get("action") or rec.get("title", "Recommendation")
                reason = rec.get("reason") or rec.get("description", "")
                priority = rec.get("priority", "medium")

            priority_color = self._get_severity_color(priority)
            self.console.print(
                f"  {i}. [{priority_color}]●[/{priority_color}] [yellow]{action}[/yellow]"
            )
            self.console.print(f"     {reason}\n")

    def render_summary_table(self, data: dict[str, Any], title: str = "Summary") -> None:
        """
        Render a simple key-value summary table.

        Args:
            data: Dictionary of key-value pairs
            title: Table title
        """
        table = Table(title=title, show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        for key, value in data.items():
            # Format key (replace underscores, capitalize)
            formatted_key = key.replace("_", " ").title()
            table.add_row(formatted_key, str(value))

        self.console.print(table)

    def render_directory_tree(
        self, structure: list[dict[str, Any]], title: str = "Directory Structure"
    ) -> None:
        """
        Render directory structure as a tree.

        Args:
            structure: List of directory info dicts with 'path' and optionally 'purpose'
            title: Tree title
        """
        tree = Tree(f"[bold]{title}[/bold]")

        for item in structure:
            path = item.get("path", "")
            purpose = item.get("purpose", "")

            if purpose:
                branch = tree.add(f"[cyan]{path}[/cyan] - {purpose}")
            else:
                branch = tree.add(f"[cyan]{path}[/cyan]")

            # Add key files if available
            if "key_files" in item:
                for file in item["key_files"]:
                    branch.add(f"[dim]{file}[/dim]")

        self.console.print(tree)

    def render_progress_spinner(self, message: str = "Processing...") -> Progress:
        """
        Create and return a progress spinner.

        Args:
            message: Progress message

        Returns:
            Rich Progress object for context manager use
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            console=self.console,
        )
        progress.add_task(message, total=None)
        return progress

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"[green]✓[/green] {message}")

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[red]✗[/red] {message}")

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {message}")

    def print_info(self, message: str) -> None:
        """Print an info message."""
        self.console.print(f"[blue]ℹ[/blue] {message}")

    def print_header(self, text: str, emoji: str = "📊") -> None:
        """Print a formatted header."""
        self.console.print(f"\n[bold]{emoji}  {text}[/bold]\n")

    # === Helper Methods ===

    @staticmethod
    def _get_severity_color(severity: str | Severity) -> str:
        """Get color for severity level."""
        severity_str = str(severity).lower()
        colors = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "blue",
            "info": "dim",
        }
        return colors.get(severity_str, "white")

    @staticmethod
    def _calculate_grade(score: int) -> str:
        """Calculate letter grade from score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
