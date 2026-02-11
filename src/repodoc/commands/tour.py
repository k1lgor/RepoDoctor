"""Tour command: Generate onboarding documentation."""

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from repodoc.commands.base import (
    console,
    get_repo_root,
    handle_command_error,
)
from repodoc.core.copilot import CopilotInvoker
from repodoc.core.logger import get_logger
from repodoc.core.parser import OutputParser
from repodoc.prompts import get_prompt_loader
from repodoc.renderers.command_renderers import TourRenderer
from repodoc.renderers.terminal_renderer import TerminalRenderer
from repodoc.schemas.tour import TourOutput

logger = get_logger()


def tour(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output JSON summary instead of generating TOUR.md")
    ] = False,
    out: Annotated[
        str | None,
        typer.Option("--out", "-o", help="Custom output path for TOUR.md (default: TOUR.md)"),
    ] = None,
    timeout: Annotated[
        int | None, typer.Option("--timeout", help="Timeout in seconds for Copilot CLI")
    ] = None,
) -> None:
    """🌎 Generate a comprehensive onboarding guide (TOUR.md).

    Creates a guided tour of the repository with architecture overview,
    entry points, key directories, and navigation tips for new contributors.

    By default, generates TOUR.md in the repository root.

    \b
    Examples:
      $ repodoc tour                           # Generate TOUR.md (default)
      $ repodoc tour --out docs/ONBOARDING.md  # Save to custom path
      $ repodoc tour --json                    # Output JSON summary instead
    """
    try:
        repo_root = get_repo_root()

        if verbose:
            console.print(f"[dim]Generating tour for: {repo_root}[/dim]")

        # Load prompt template
        prompt_loader = get_prompt_loader()
        prompt = prompt_loader.get_prompt("tour", repo_path=str(repo_root))

        # Invoke Copilot CLI
        copilot = CopilotInvoker(timeout=timeout)

        if not json_output:
            with console.status("[bold blue]Generating repository tour...[/bold blue]"):
                raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)
        else:
            # Silent mode for JSON output
            raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)

        # Parse and validate output
        parser = OutputParser()
        result = parser.parse_and_validate(raw_output, TourOutput)

        # Handle JSON output
        if json_output:
            console.print_json(result.tour.model_dump_json(indent=2))
            return

        # Generate TOUR.md
        tour_path = Path(out) if out else repo_root / "TOUR.md"

        # Render human-readable output using dedicated renderer
        terminal = TerminalRenderer(verbose=verbose, console=console)
        renderer = TourRenderer(terminal)
        renderer.render(result, str(tour_path))

    except ValidationError as e:
        logger.error(f"Failed to validate tour output: {e}")
        console.print("[red]✗ Failed to parse Copilot output[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from None
    except typer.Exit:
        # Let typer.Exit propagate without handling
        raise
    except Exception as e:
        handle_command_error(e, verbose)
