"""Report command: Generate markdown reports from scan results."""

import json
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from repodoc.commands.base import (
    console,
    ensure_repodoc_dir,
    get_repo_root,
    handle_command_error,
    print_success_message,
)
from repodoc.core.copilot import CopilotInvoker
from repodoc.core.logger import get_logger
from repodoc.core.parser import OutputParser
from repodoc.prompts import get_prompt_loader
from repodoc.schemas.report import ReportOutput

logger = get_logger()


def report(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    out: Annotated[
        str | None,
        typer.Option("--out", "-o", help="Custom output path (default: REPODOCTOR_REPORT.md)"),
    ] = None,
    format_type: Annotated[
        str, typer.Option("--format", help="Report format: markdown or html")
    ] = "markdown",
    timeout: Annotated[
        int | None, typer.Option("--timeout", help="Timeout in seconds for Copilot CLI")
    ] = None,
) -> None:
    """📋 Generate a comprehensive markdown report from scan results.

    Uses the last scan results cached in .repodoc/last_scan.json to generate
    a formatted report with findings, recommendations, and health scores.
    """
    try:
        repo_root = get_repo_root()
        repodoc_dir = ensure_repodoc_dir(repo_root)

        if verbose:
            console.print(f"[dim]Generating report for: {repo_root}[/dim]")

        # Validate format
        valid_formats = ["markdown", "html"]
        if format_type not in valid_formats:
            console.print(
                f"[red]✗ Error:[/red] Invalid format. Must be one of: {', '.join(valid_formats)}"
            )
            raise typer.Exit(code=1)

        # Load cached scan results
        scan_cache_path = repodoc_dir / "last_scan.json"

        if not scan_cache_path.exists():
            console.print(
                "[red]✗ Error:[/red] No scan results found. Run [cyan]repodoc scan[/cyan] first."
            )
            raise typer.Exit(code=1)

        try:
            with open(scan_cache_path, encoding="utf-8") as f:
                scan_data = json.load(f)
        except Exception as e:
            error_msg = f"Failed to load scan results: {e}"
            logger.error(error_msg)
            console.print(f"[red]✗ {error_msg}[/red]")
            raise typer.Exit(code=1) from e

        # Load prompt template with scan data
        prompt_loader = get_prompt_loader()
        prompt = prompt_loader.get_prompt(
            "report",
            repo_path=str(repo_root),
            scan_data=json.dumps(scan_data, indent=2),
            format=format_type,
        )

        # Invoke Copilot CLI to generate report
        copilot = CopilotInvoker(timeout=timeout)

        with console.status("[bold blue]Generating report...[/bold blue]"):
            raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)

        # Parse and validate output
        parser = OutputParser()
        result = parser.parse_and_validate(raw_output, ReportOutput)

        # Determine output path
        if out:
            report_path = Path(out)
        else:
            extension = "md" if format_type == "markdown" else "html"
            report_path = repo_root / f"REPODOCTOR_REPORT.{extension}"

        # Write report to file
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(result.markdown_content)

            console.print(f"\n[green]✓[/green] Report generated: {report_path}")

            # Show metadata
            console.print(f"[cyan]Report Title:[/cyan] {result.report_title}")
            console.print(f"[cyan]Generated:[/cyan] {result.generation_timestamp}")

        except Exception as e:
            error_msg = f"Failed to write report: {e}"
            logger.error(error_msg)
            console.print(f"[red]✗ {error_msg}[/red]")
            raise typer.Exit(code=1) from e

        # Show success message with next actions
        next_actions = [
            "Review the full report for detailed findings",
            "Address high-priority issues identified in the report",
            "Share the report with your team for collaborative review",
            "Re-run 'repodoc scan' after making improvements",
        ]
        print_success_message("Report generation", next_actions)

    except ValidationError as e:
        logger.error(f"Failed to validate report output: {e}")
        console.print("[red]✗ Failed to parse Copilot output[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from None
    except typer.Exit:
        # Let typer.Exit propagate without handling
        raise
    except Exception as e:
        handle_command_error(e, verbose)
