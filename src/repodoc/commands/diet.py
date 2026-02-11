"""Diet command: Analyze repository bloat and hygiene."""

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from repodoc.commands.base import (
    console,
    get_repo_root,
    handle_command_error,
    print_success_message,
)
from repodoc.core.copilot import CopilotInvoker
from repodoc.core.logger import get_logger
from repodoc.core.parser import OutputParser
from repodoc.prompts import get_prompt_loader
from repodoc.renderers.command_renderers import DietRenderer
from repodoc.renderers.terminal_renderer import TerminalRenderer
from repodoc.schemas.diet import DietOutput

logger = get_logger()


def diet(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output JSON summary instead of generating DIET.md")
    ] = False,
    out: Annotated[
        str | None,
        typer.Option("--out", "-o", help="Custom output path for DIET.md (default: DIET.md)"),
    ] = None,
    timeout: Annotated[
        int | None, typer.Option("--timeout", help="Timeout in seconds for Copilot CLI")
    ] = None,
) -> None:
    """🍔 Analyze repository bloat and hygiene issues.

    Generates a comprehensive diet analysis documenting repository size,
    largest files/directories, suspected artifacts, and missing hygiene files.

    By default, generates DIET.md in the repository root.

    \b
    Examples:
      $ repodoc diet                        # Generate DIET.md (default)
      $ repodoc diet --out docs/BLOAT.md   # Save to custom path
      $ repodoc diet --json                 # Output JSON summary instead

    \b
    What it analyzes:
      • Largest files in the repository
      • Potentially unused dependencies
      • Missing hygiene files (.gitignore, LICENSE, etc.)
      • Overall repository size and health
    """
    try:
        repo_root = get_repo_root()

        if verbose and not json_output:
            console.print(f"[dim]Running diet analysis on: {repo_root}[/dim]")

        # Load prompt template
        prompt_loader = get_prompt_loader()
        prompt = prompt_loader.get_prompt("diet", repo_path=str(repo_root))

        # Invoke Copilot CLI
        copilot = CopilotInvoker(timeout=timeout)

        if not json_output:
            with console.status("[bold blue]🔍 Analyzing repository bloat...[/bold blue]"):
                raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)
        else:
            # Silent mode for JSON output
            raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)

        # Parse and validate output
        parser = OutputParser()
        result = parser.parse_and_validate(raw_output, DietOutput)

        # Handle JSON output
        if json_output:
            console.print_json(result.analysis.model_dump_json(indent=2))
            return

        # Generate DIET.md
        diet_path = Path(out) if out else repo_root / "DIET.md"

        # Write the DIET.md file
        try:
            with open(diet_path, "w", encoding="utf-8") as f:
                f.write(result.diet_markdown)
            if not json_output:
                console.print(f"[green]✓[/green] Generated diet analysis: {diet_path}")
        except Exception as e:
            error_msg = f"Failed to write diet file: {e}"
            logger.error(error_msg)
            console.print(f"[red]✗ {error_msg}[/red]")
            raise typer.Exit(code=1) from e

        # Show terminal summary
        terminal = TerminalRenderer(verbose=verbose, console=console)
        renderer = DietRenderer(terminal)
        renderer.render(result)

        # Show success message with next actions
        next_actions = [
            "Review identified bloat and consider cleanup",
            "Add missing hygiene files to improve repo health",
            "Run 'repodoc scan' for a full health check",
        ]
        print_success_message("Diet analysis", next_actions)

    except ValidationError as e:
        logger.error(f"Failed to validate diet output: {e}")
        console.print("[red]✗ Failed to parse Copilot output[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from None
    except typer.Exit:
        # Let typer.Exit propagate without handling
        raise
    except Exception as e:
        handle_command_error(e, verbose)
