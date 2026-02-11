"""Deadcode command: Detect unused code with confidence levels."""

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from repodoc.commands.base import (
    console,
    get_repo_root,
    handle_command_error,
    handle_json_flag,
    save_text_output,
)
from repodoc.core.copilot import CopilotInvoker
from repodoc.core.logger import get_logger
from repodoc.core.parser import OutputParser
from repodoc.prompts import get_prompt_loader
from repodoc.renderers.command_renderers import DeadCodeRenderer
from repodoc.renderers.terminal_renderer import TerminalRenderer
from repodoc.schemas.deadcode import DeadCodeOutput

logger = get_logger()


def deadcode(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON instead of formatted text")
    ] = False,
    out: Annotated[
        str | None, typer.Option("--out", "-o", help="Save output to specified file")
    ] = None,
    min_confidence: Annotated[
        str,
        typer.Option(
            "--min-confidence", help="Minimum confidence level to report (low, medium, high)"
        ),
    ] = "medium",
    timeout: Annotated[
        int | None, typer.Option("--timeout", help="Timeout in seconds for Copilot CLI")
    ] = None,
) -> None:
    """💀 Detect potentially dead code with confidence levels.

    Identifies unused functions, classes, imports, and files based on
    static analysis. Results include confidence levels for each finding.
    """
    try:
        repo_root = get_repo_root()

        # Validate confidence level
        valid_levels = ["low", "medium", "high"]
        if min_confidence not in valid_levels:
            console.print(
                f"[red]✗ Error:[/red] Invalid confidence level. "
                f"Must be one of: {', '.join(valid_levels)}"
            )
            raise typer.Exit(code=1)

        if verbose:
            console.print(f"[dim]Detecting dead code in: {repo_root}[/dim]")

        # Load prompt template
        prompt_loader = get_prompt_loader()
        prompt = prompt_loader.get_prompt("deadcode", repo_path=str(repo_root))

        # Invoke Copilot CLI
        copilot = CopilotInvoker(timeout=timeout)

        if not json_output:
            with console.status("[bold blue]Analyzing codebase for dead code...[/bold blue]"):
                raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)
        else:
            # Silent mode for JSON output
            raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)

        # Parse and validate output
        parser = OutputParser()
        result = parser.parse_and_validate(raw_output, DeadCodeOutput)

        # Handle JSON output (to stdout or file if --out specified)
        if json_output:
            handle_json_flag(result.model_dump(), json_output, out)
            return

        # Render human-readable output to terminal
        terminal = TerminalRenderer(verbose=verbose, console=console)
        renderer = DeadCodeRenderer(terminal)
        renderer.render(result, min_confidence)

        # If --out specified (without --json), save formatted text to file
        if out:
            save_text_output(
                Path(out),
                renderer.render,
                result,
                min_confidence,
                terminal=terminal,
                verbose=verbose,
            )

    except ValidationError as e:
        logger.error(f"Failed to validate deadcode output: {e}")
        console.print("[red]✗ Failed to parse Copilot output[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from None
    except typer.Exit:
        # Let typer.Exit propagate without handling
        raise
    except Exception as e:
        handle_command_error(e, verbose)
