"""Docker command: Analyze and optimize Dockerfiles."""

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
from repodoc.renderers.command_renderers import DockerRenderer
from repodoc.renderers.terminal_renderer import TerminalRenderer
from repodoc.schemas.docker import DockerOutput

logger = get_logger()


def docker(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON instead of formatted text")
    ] = False,
    out: Annotated[
        str | None, typer.Option("--out", "-o", help="Save output to specified file")
    ] = None,
    fix: Annotated[
        bool, typer.Option("--fix", help="Generate optimized Dockerfile.repodoc with fixes applied")
    ] = False,
    in_place: Annotated[
        bool,
        typer.Option(
            "--in-place", help="Overwrite original Dockerfile (dangerous, requires --fix)"
        ),
    ] = False,
    timeout: Annotated[
        int | None, typer.Option("--timeout", help="Timeout in seconds for Copilot CLI")
    ] = None,
) -> None:
    """🐳 Analyze Dockerfile for security and optimization issues.

    Identifies security vulnerabilities, performance issues, and best practice
    violations in Dockerfiles. Can generate patched version with --fix.
    """
    try:
        repo_root = get_repo_root()

        # Validate flag combinations
        if in_place and not fix:
            console.print("[red]✗ Error:[/red] --in-place requires --fix")
            raise typer.Exit(code=1)

        if verbose:
            console.print(f"[dim]Analyzing Dockerfile in: {repo_root}[/dim]")

        # Check if Dockerfile exists
        dockerfile_path = repo_root / "Dockerfile"
        if not dockerfile_path.exists():
            console.print("[red]✗ Error:[/red] No Dockerfile found in repository root")
            raise typer.Exit(code=1)

        # Load prompt template
        prompt_loader = get_prompt_loader()
        prompt = prompt_loader.get_prompt(
            "docker", repo_path=str(repo_root), dockerfile_path=str(dockerfile_path)
        )

        # Invoke Copilot CLI
        copilot = CopilotInvoker(timeout=timeout)

        if not json_output:
            with console.status("[bold blue]Analyzing Dockerfile...[/bold blue]"):
                raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)
        else:
            # Silent mode for JSON output
            raw_output, _ = copilot.invoke_with_retry(prompt, cwd=repo_root)

        # Parse and validate output
        parser = OutputParser()
        result = parser.parse_and_validate(raw_output, DockerOutput)

        # Handle JSON output (to stdout or file if --out specified)
        if json_output:
            handle_json_flag(result.model_dump(), json_output, out)
            return

        # Handle --fix flag
        patched_path_str = None
        if fix and result.patched_dockerfile:
            if in_place:
                # Overwrite original Dockerfile
                target_path = dockerfile_path
                console.print("[yellow]⚠ Warning:[/yellow] Overwriting original Dockerfile")
            else:
                # Safe default: write to Dockerfile.repodoc
                target_path = repo_root / "Dockerfile.repodoc"

            try:
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(result.patched_dockerfile.patched_content)

                console.print(f"\n[green]✓[/green] Patched Dockerfile written to: {target_path}")
                patched_path_str = str(target_path)

                if result.patched_dockerfile.changes_summary:
                    console.print("\n[bold]Changes Applied:[/bold]")
                    for change in result.patched_dockerfile.changes_summary:
                        console.print(f"  • {change}")

            except Exception as e:
                error_msg = f"Failed to write patched Dockerfile: {e}"
                logger.error(error_msg)
                console.print(f"[red]✗ {error_msg}[/red]")
                raise typer.Exit(code=1) from e

        # Render human-readable output using dedicated renderer
        terminal = TerminalRenderer(verbose=verbose, console=console)
        renderer = DockerRenderer(terminal)
        renderer.render(result, patched_path_str)

        # If --out specified (without --json), save formatted text to file
        if out:
            save_text_output(
                Path(out),
                renderer.render,
                result,
                patched_path_str,
                terminal=terminal,
                verbose=verbose
            )

    except ValidationError as e:
        logger.error(f"Failed to validate docker output: {e}")
        console.print("[red]✗ Failed to parse Copilot output[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from None
    except typer.Exit:
        # Let typer.Exit propagate without handling
        raise
    except Exception as e:
        handle_command_error(e, verbose)
