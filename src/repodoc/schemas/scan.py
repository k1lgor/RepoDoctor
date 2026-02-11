"""Schemas for the 'scan' command (aggregated results)."""

from pydantic import BaseModel, Field

from repodoc.schemas.base import BaseCommandOutput, Issue, Recommendation, RepoHealthScore
from repodoc.schemas.deadcode import DeadCodeSummary
from repodoc.schemas.diet import BloatAnalysis
from repodoc.schemas.docker import DockerfileAnalysis
from repodoc.schemas.tour import TourSummary


class ModuleResult(BaseModel):
    """Result from a single scan module."""

    module_name: str = Field(..., description="Name of the module (e.g., 'diet', 'docker')")
    success: bool = Field(..., description="Whether the module completed successfully")
    issues_count: int = Field(0, description="Number of issues found by this module")
    score: int | None = Field(None, description="Module-specific score, if applicable")
    error: str | None = Field(None, description="Error message if module failed")


class ScanResult(BaseModel):
    """Aggregated results from a full repository scan."""

    health_score: RepoHealthScore = Field(..., description="Overall repository health score")
    module_results: list[ModuleResult] = Field(
        default_factory=list, description="Results from each scan module"
    )
    diet_analysis: BloatAnalysis | None = Field(None, description="Diet module results")
    tour_summary: TourSummary | None = Field(None, description="Tour module results")
    docker_analysis: list[DockerfileAnalysis] = Field(
        default_factory=list, description="Docker module results"
    )
    deadcode_summary: DeadCodeSummary | None = Field(None, description="Dead code module results")


class ScanOutput(BaseCommandOutput):
    """Output schema for 'repodoc scan' command."""

    command: str = Field(default="scan")
    scan_result: ScanResult = Field(..., description="Aggregated scan results")
    top_issues: list[Issue] = Field(
        default_factory=list, description="Top priority issues across all modules"
    )
    top_recommendations: list[Recommendation] = Field(
        default_factory=list, description="Top priority recommendations"
    )
    next_actions: list[str] = Field(
        default_factory=list, description="Immediate next actions to take"
    )
