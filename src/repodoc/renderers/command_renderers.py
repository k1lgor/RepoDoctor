"""Specialized renderers for specific command outputs."""

from typing import Any

from repodoc.renderers.terminal_renderer import TerminalRenderer
from repodoc.schemas.deadcode import DeadCodeOutput
from repodoc.schemas.diet import DietOutput
from repodoc.schemas.docker import DockerOutput
from repodoc.schemas.scan import ScanResult
from repodoc.schemas.tour import TourOutput


class DietRenderer:
    """Renders diet analysis output."""

    def __init__(self, terminal: TerminalRenderer) -> None:
        self.terminal = terminal

    def render(self, result: DietOutput) -> None:
        """Render diet analysis results."""
        self.terminal.print_header("Diet Analysis Results", "🍽️")

        # Bloat summary
        if result.analysis:
            analysis = result.analysis
            summary_data = {
                "Total Size": analysis.total_size_human,
                "Total Bytes": f"{analysis.total_size_bytes:,}",
                "Largest Files": len(analysis.largest_files),
                "Suspected Artifacts": len(analysis.suspected_artifacts),
                "Missing Hygiene Files": len(analysis.missing_hygiene_files),
            }
            self.terminal.render_summary_table(summary_data, "Repository Size Summary")

            # Largest files
            if analysis.largest_files:
                self.terminal.console.print("\n[bold yellow]Largest Files:[/bold yellow]")
                for file_info in analysis.largest_files[:10]:
                    self.terminal.console.print(
                        f"  • {file_info.path} - [yellow]{file_info.size_human}[/yellow]"
                    )

            # Missing hygiene files
            if analysis.missing_hygiene_files:
                self.terminal.console.print("\n[bold red]Missing Hygiene Files:[/bold red]")
                for missing in analysis.missing_hygiene_files:
                    self.terminal.console.print(f"  • {missing.filename}: {missing.importance}")

            # Suspected artifacts
            if analysis.suspected_artifacts:
                self.terminal.console.print("\n[bold magenta]Suspected Artifacts:[/bold magenta]")
                for artifact in analysis.suspected_artifacts[:10]:
                    self.terminal.console.print(f"  • [dim]{artifact}[/dim]")

        # Issues and recommendations
        if result.issues:
            self.terminal.console.print()
            self.terminal.render_issues_table(result.issues, "Diet Issues")

        if result.recommendations:
            self.terminal.render_recommendations(result.recommendations)

        self.terminal.print_success("Diet analysis complete")


class TourRenderer:
    """Renders tour generation output."""

    def __init__(self, terminal: TerminalRenderer) -> None:
        self.terminal = terminal

    def render(self, result: TourOutput, tour_path: str) -> None:
        """Render tour generation results and save TOUR.md file."""
        from pathlib import Path

        # Write the TOUR.md file
        tour_file = Path(tour_path)
        try:
            with open(tour_file, "w", encoding="utf-8") as f:
                f.write(result.tour_markdown)
            self.terminal.print_success(f"Generated onboarding tour: {tour_path}")
        except Exception as e:
            self.terminal.console.print(f"[red]✗ Failed to write tour file: {e}[/red]")
            raise

        # Show summary
        if result.tour:
            tour = result.tour

            # Stack info
            if tour.stack:
                self.terminal.console.print(
                    f"\n[cyan]Languages:[/cyan] {', '.join(tour.stack.languages)}"
                )
                if tour.stack.frameworks:
                    frameworks = ", ".join(tour.stack.frameworks)
                    self.terminal.console.print(f"[cyan]Frameworks:[/cyan] {frameworks}")
                if tour.stack.tools:
                    tools = ", ".join(tour.stack.tools)
                    self.terminal.console.print(f"[cyan]Tools:[/cyan] {tools}")

            # Entry points
            if tour.entry_points:
                self.terminal.console.print("\n[bold]Entry Points:[/bold]")
                for ep in tour.entry_points[:5]:
                    self.terminal.console.print(f"  • {ep.file_path} - {ep.description}")

            # Directory structure as tree
            if tour.directory_structure:
                self.terminal.console.print()
                self.terminal.render_directory_tree(
                    [
                        {
                            "path": d.path,
                            "purpose": d.purpose,
                            "key_files": d.key_files,
                        }
                        for d in tour.directory_structure[:10]
                    ],
                    "Key Directories",
                )


class DockerRenderer:
    """Renders Docker analysis output."""

    def __init__(self, terminal: TerminalRenderer) -> None:
        self.terminal = terminal

    def render(self, result: DockerOutput, patched_path: str | None = None) -> None:
        """Render Docker analysis results."""
        self.terminal.print_header("Dockerfile Analysis Results", "🐳")

        # Analysis summary
        if result.dockerfiles:
            for analysis in result.dockerfiles:
                summary_data: dict[str, Any] = {
                    "Dockerfile": analysis.dockerfile_path,
                    "Base Image": analysis.base_image or "Not detected",
                    "Issues Found": len(analysis.issues),
                    "Missing .dockerignore": "Yes" if analysis.missing_dockerignore else "No",
                }
                if analysis.size_estimate:
                    summary_data["Estimated Size"] = analysis.size_estimate

                self.terminal.render_summary_table(summary_data, "Docker Analysis")

                # Issues by severity
                if analysis.issues:
                    self.terminal.console.print()
                    # Convert DockerIssue to dict for rendering
                    issue_dicts = []
                    for issue in analysis.issues:
                        issue_dicts.append(
                            {
                                "severity": issue.severity,
                                "category": issue.issue_type,
                                "description": (
                                    f"{issue.explanation} → "
                                    f"{issue.suggested or 'See recommendations'}"
                                ),
                                "file_path": f"Line {issue.line_number}"
                                if issue.line_number
                                else None,
                            }
                        )
                    self.terminal.render_issues_table(issue_dicts, "Dockerfile Issues")

                # Optimizations
                if analysis.optimizations:
                    self.terminal.console.print(
                        "\n[bold green]Optimization Suggestions:[/bold green]"
                    )
                    for opt in analysis.optimizations:
                        self.terminal.console.print(f"  • {opt}")

        # .dockerignore suggestions
        if result.dockerignore_suggestions:
            self.terminal.console.print("\n[bold].dockerignore Suggestions:[/bold]")
            for suggestion in result.dockerignore_suggestions:
                self.terminal.console.print(f"  • [dim]{suggestion}[/dim]")

        # Patched dockerfile info
        if patched_path:
            self.terminal.print_success(f"Patched Dockerfile written to: {patched_path}")
            if result.patched_dockerfile and result.patched_dockerfile.changes_summary:
                self.terminal.console.print("\n[bold]Changes Applied:[/bold]")
                for change in result.patched_dockerfile.changes_summary:
                    self.terminal.console.print(f"  • {change}")

        # Recommendations
        if result.recommendations:
            self.terminal.render_recommendations(result.recommendations)

        self.terminal.print_success("Dockerfile analysis complete")


class DeadCodeRenderer:
    """Renders dead code analysis output."""

    def __init__(self, terminal: TerminalRenderer) -> None:
        self.terminal = terminal

    def render(self, result: DeadCodeOutput, min_confidence: str = "medium") -> None:
        """Render dead code analysis results."""
        self.terminal.print_header("Dead Code Analysis Results", "🔍")

        # Summary
        if result.summary:
            summary = result.summary
            summary_data = {
                "Total Findings": summary.total_findings,
                "High Confidence": summary.high_confidence_count,
                "Medium Confidence": summary.medium_confidence_count,
                "Low Confidence": summary.low_confidence_count,
                "Estimated Dead Lines": summary.estimated_total_lines,
            }
            self.terminal.render_summary_table(summary_data, "Dead Code Summary")

        # Findings by confidence level
        if result.findings:
            confidence_groups = {"high": [], "medium": [], "low": []}
            for finding in result.findings:
                confidence_groups[finding.confidence].append(finding)

            confidence_order = {"high": 3, "medium": 2, "low": 1}
            min_level = confidence_order[min_confidence]

            for conf_level in ["high", "medium", "low"]:
                if confidence_order[conf_level] < min_level:
                    continue

                level_findings = confidence_groups[conf_level]
                if level_findings:
                    self.terminal.console.print()
                    from rich.table import Table

                    table = Table(
                        title=f"{conf_level.capitalize()} Confidence Dead Code",
                        show_header=True,
                        header_style="bold magenta",
                    )
                    table.add_column("Type", style="cyan", width=15)
                    table.add_column("File", style="yellow", width=35)
                    table.add_column("Lines", style="white", width=12)
                    table.add_column("Reason", no_wrap=False)

                    for finding in level_findings:
                        lines_display = (
                            f"{finding.line_range[0]}-{finding.line_range[1]}"
                            if finding.line_range
                            else "N/A"
                        )
                        table.add_row(
                            finding.code_type, finding.file_path, lines_display, finding.reason
                        )

                    self.terminal.console.print(table)

        # Recommendations
        if result.recommendations:
            self.terminal.render_recommendations(result.recommendations)

        self.terminal.print_success("Dead code analysis complete")


class ScanRenderer:
    """Renders full scan results."""

    def __init__(self, terminal: TerminalRenderer) -> None:
        self.terminal = terminal

    def render(self, result: ScanResult) -> None:
        """Render scan results summary."""
        self.terminal.print_header("Scan Summary", "📊")

        # Overall health score
        self.terminal.render_health_score(result.health_score, "Overall Repository Health")

        # Module summaries
        summary_data: dict[str, str] = {}

        if result.diet_analysis:
            diet = result.diet_analysis
            summary_data["Diet"] = f"{diet.total_size_human}, {len(diet.largest_files)} large files"

        if result.tour_summary:
            tour = result.tour_summary
            summary_data["Tour"] = (
                f"{len(tour.entry_points)} entry points, "
                f"{len(tour.directory_structure)} directories"
            )

        if result.docker_analysis:
            total_issues = sum(len(d.issues) for d in result.docker_analysis)
            summary_data["Docker"] = f"{total_issues} issues found"

        if result.deadcode_summary:
            summary = result.deadcode_summary
            summary_data["Dead Code"] = f"{summary.total_findings} findings"

        if summary_data:
            self.terminal.console.print()
            self.terminal.render_summary_table(summary_data, "Module Results")

        self.terminal.print_success("Full scan complete")
