"""Scan command: Full repository health analysis."""

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
    handle_json_flag,
    save_text_output,
)
from repodoc.core.copilot import CopilotInvoker
from repodoc.core.logger import get_logger
from repodoc.core.parser import OutputParser
from repodoc.prompts import get_prompt_loader
from repodoc.renderers.command_renderers import ScanRenderer
from repodoc.renderers.terminal_renderer import TerminalRenderer
from repodoc.schemas.base import RepoHealthScore
from repodoc.schemas.deadcode import DeadCodeOutput
from repodoc.schemas.diet import DietOutput
from repodoc.schemas.docker import DockerOutput
from repodoc.schemas.scan import ScanResult
from repodoc.schemas.tour import TourOutput

logger = get_logger()


def scan(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON instead of formatted text")
    ] = False,
    out: Annotated[
        str | None, typer.Option("--out", "-o", help="Save output to specified file")
    ] = None,
    skip_docker: Annotated[
        bool, typer.Option("--skip-docker", help="Skip Dockerfile analysis")
    ] = False,
    skip_deadcode: Annotated[
        bool, typer.Option("--skip-deadcode", help="Skip dead code analysis")
    ] = False,
    timeout: Annotated[
        int | None, typer.Option("--timeout", help="Timeout in seconds for Copilot CLI")
    ] = None,
) -> None:
    """🔬 Run comprehensive repository health scan.

    Performs a full analysis of your repository including bloat detection,
    code quality checks, Docker configuration, and dead code detection.

    \b
    Examples:
      $ repodoc scan                     # Run full scan
      $ repodoc scan --skip-docker       # Skip Docker analysis
      $ repodoc scan --json              # Get JSON output
      $ repodoc scan --out results.json  # Save results to file

    \b
    What it analyzes:
      • Repository bloat and hygiene (diet module)
      • Onboarding documentation (tour module)
      • Dockerfile security and optimization (docker module)
      • Dead code detection (deadcode module)
      • Overall repository health score

    \b
    💡 Tip:
      Results are cached in .repodoc/ directory.
      Use 'repodoc report' to generate a markdown report.
    """
    try:
        repo_root = get_repo_root()
        repodoc_dir = ensure_repodoc_dir(repo_root)

        if not json_output:
            console.print("\n[bold]🏥 RepoDoctor Full Scan[/bold]\n")

        if verbose and not json_output:
            console.print(f"[dim]Scanning repository: {repo_root}[/dim]\n")

        copilot = CopilotInvoker(timeout=timeout)
        parser = OutputParser()
        prompt_loader = get_prompt_loader()

        # Initialize component results
        diet_result = None
        tour_result = None
        docker_result = None
        deadcode_result = None

        # Module 1: Diet Analysis
        if not json_output:
            console.print("[bold cyan]1/4[/bold cyan] Running diet analysis...")
        try:
            diet_prompt = prompt_loader.get_prompt("diet", repo_path=str(repo_root))
            diet_output, _ = copilot.invoke_with_retry(diet_prompt, cwd=repo_root)
            diet_result = parser.parse_and_validate(diet_output, DietOutput)
            if not json_output:
                console.print("     [green]✓[/green] Diet analysis complete\n")
        except Exception as e:
            logger.error(f"Diet analysis failed: {e}")
            if not json_output:
                console.print(f"     [yellow]⚠[/yellow] Diet analysis failed: {e}\n")

        # Module 2: Tour Generation
        if not json_output:
            console.print("[bold cyan]2/4[/bold cyan] Generating repository tour...")
        try:
            tour_prompt = prompt_loader.get_prompt("tour", repo_path=str(repo_root))
            tour_output, _ = copilot.invoke_with_retry(tour_prompt, cwd=repo_root)
            tour_result = parser.parse_and_validate(tour_output, TourOutput)
            if not json_output:
                console.print("     [green]✓[/green] Tour generation complete\n")
        except Exception as e:
            logger.error(f"Tour generation failed: {e}")
            if not json_output:
                console.print(f"     [yellow]⚠[/yellow] Tour generation failed: {e}\n")

        # Module 3: Docker Analysis (optional)
        if not skip_docker:
            if not json_output:
                console.print("[bold cyan]3/4[/bold cyan] Analyzing Dockerfile...")
            dockerfile_path = repo_root / "Dockerfile"

            if dockerfile_path.exists():
                try:
                    docker_prompt = prompt_loader.get_prompt(
                        "docker", repo_path=str(repo_root), dockerfile_path=str(dockerfile_path)
                    )
                    docker_output, _ = copilot.invoke_with_retry(docker_prompt, cwd=repo_root)
                    docker_result = parser.parse_and_validate(docker_output, DockerOutput)
                    if not json_output:
                        console.print("     [green]✓[/green] Docker analysis complete\n")
                except Exception as e:
                    logger.error(f"Docker analysis failed: {e}")
                    if not json_output:
                        console.print(f"     [yellow]⚠[/yellow] Docker analysis failed: {e}\n")
            else:
                if not json_output:
                    console.print("     [dim]⊘[/dim] No Dockerfile found, skipping\n")
        else:
            if not json_output:
                console.print("[bold cyan]3/4[/bold cyan] Skipping Docker analysis\n")

        # Module 4: Dead Code Analysis (optional)
        if not skip_deadcode:
            if not json_output:
                console.print("[bold cyan]4/4[/bold cyan] Detecting dead code...")
            try:
                deadcode_prompt = prompt_loader.get_prompt("deadcode", repo_path=str(repo_root))
                deadcode_output, _ = copilot.invoke_with_retry(deadcode_prompt, cwd=repo_root)
                deadcode_result = parser.parse_and_validate(deadcode_output, DeadCodeOutput)
                if not json_output:
                    console.print("     [green]✓[/green] Dead code analysis complete\n")
            except Exception as e:
                logger.error(f"Dead code analysis failed: {e}")
                if not json_output:
                    console.print(f"     [yellow]⚠[/yellow] Dead code analysis failed: {e}\n")
        else:
            if not json_output:
                console.print("[bold cyan]4/4[/bold cyan] Skipping dead code analysis\n")

        # Calculate overall health score
        scores = []
        # Individual command outputs don't have health_score, so we estimate based on issues
        if diet_result:
            diet_score = max(0, 100 - (len(diet_result.issues) * 5))
            scores.append(diet_score)
        if docker_result:
            docker_score = max(0, 100 - (len(docker_result.issues) * 5))
            scores.append(docker_score)
        if deadcode_result and deadcode_result.summary:
            deadcode_score = max(0, 100 - (deadcode_result.summary.total_findings * 2))
            scores.append(deadcode_score)

        overall_score_value = sum(scores) / len(scores) if scores else 0.0

        # Determine grade
        if overall_score_value >= 90:
            grade = "A"
        elif overall_score_value >= 80:
            grade = "B"
        elif overall_score_value >= 70:
            grade = "C"
        elif overall_score_value >= 60:
            grade = "D"
        else:
            grade = "F"

        overall_health = RepoHealthScore(overall_score=int(overall_score_value), grade=grade)

        # Build scan result matching schema
        scan_result = ScanResult(
            health_score=overall_health,
            diet_analysis=diet_result.analysis if diet_result else None,
            tour_summary=tour_result.tour if tour_result else None,
            docker_analysis=docker_result.dockerfiles if docker_result else [],
            deadcode_summary=deadcode_result.summary if deadcode_result else None,
        )

        # Save scan results to cache
        scan_cache_path = repodoc_dir / "last_scan.json"
        try:
            with open(scan_cache_path, "w", encoding="utf-8") as f:
                json.dump(scan_result.model_dump(), f, indent=2)
            logger.info(f"Saved scan results to {scan_cache_path}")
        except Exception as e:
            logger.warning(f"Failed to save scan cache: {e}")

        # Handle JSON output (to stdout or file if --out specified)
        if json_output:
            handle_json_flag(scan_result.model_dump(), json_output, out)
            return

        # Render summary using dedicated renderer
        terminal = TerminalRenderer(verbose=verbose, console=console)
        renderer = ScanRenderer(terminal)
        renderer.render(scan_result)

        # If --out specified (without --json), save formatted text to file
        if out:
            save_text_output(
                Path(out),
                renderer.render,
                scan_result,
                terminal=terminal,
                verbose=verbose
            )

        # Show success message with next actions
        from repodoc.commands.base import print_success_message

        if not json_output:
            terminal.console.print(f"\n[dim]Results cached at: {scan_cache_path}[/dim]")

        next_actions = [
            "Review the health score and identified issues",
            "Run 'repodoc report' to generate a detailed markdown report",
            "Address critical/high severity issues first",
        ]
        print_success_message("Full repository scan", next_actions)

    except ValidationError as e:
        logger.error(f"Failed to validate scan output: {e}")
        console.print("[red]✗ Failed to parse Copilot output[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from None
    except typer.Exit:
        # Let typer.Exit propagate without handling
        raise
    except Exception as e:
        handle_command_error(e, verbose)
