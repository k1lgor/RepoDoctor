"""Schemas for the 'docker' command."""

from pydantic import BaseModel, Field

from repodoc.schemas.base import BaseCommandOutput, Severity


class DockerIssue(BaseModel):
    """Specific issue found in a Dockerfile."""

    issue_type: str = Field(..., description="Type of issue (e.g., 'caching', 'security', 'size')")
    line_number: int | None = Field(None, description="Line number in Dockerfile")
    current: str = Field(..., description="Current problematic code or configuration")
    suggested: str | None = Field(None, description="Suggested improvement")
    explanation: str = Field(..., description="Why this is an issue")
    severity: Severity = Field(..., description="Severity of this Docker issue")


class DockerfileAnalysis(BaseModel):
    """Analysis of a Dockerfile."""

    dockerfile_path: str = Field(..., description="Path to the Dockerfile")
    base_image: str | None = Field(None, description="Base image used (FROM directive)")
    issues: list[DockerIssue] = Field(default_factory=list, description="Issues found")
    optimizations: list[str] = Field(
        default_factory=list, description="General optimization suggestions"
    )
    missing_dockerignore: bool = Field(False, description="Whether .dockerignore is missing")
    size_estimate: str | None = Field(None, description="Estimated image size, if calculable")


class PatchedDockerfile(BaseModel):
    """Patched/improved Dockerfile content."""

    original_path: str = Field(..., description="Path to original Dockerfile")
    patched_content: str = Field(..., description="Improved Dockerfile content")
    changes_summary: list[str] = Field(default_factory=list, description="List of changes made")


class DockerOutput(BaseCommandOutput):
    """Output schema for 'repodoc docker' command."""

    command: str = Field(default="docker")
    dockerfiles: list[DockerfileAnalysis] = Field(
        default_factory=list, description="Analysis of each Dockerfile found"
    )
    patched_dockerfile: PatchedDockerfile | None = Field(
        None, description="Patched Dockerfile (if --fix was used)"
    )
    dockerignore_suggestions: list[str] = Field(
        default_factory=list, description="Patterns to add to .dockerignore"
    )
