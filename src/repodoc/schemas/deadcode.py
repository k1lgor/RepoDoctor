"""Schemas for the 'deadcode' command."""

from pydantic import BaseModel, Field

from repodoc.schemas.base import BaseCommandOutput, ConfidenceLevel


class DeadCodeFinding(BaseModel):
    """A single dead code finding."""

    file_path: str = Field(..., description="Path to the file containing dead code")
    line_range: tuple[int, int] | None = Field(
        None, description="Start and end line numbers, if applicable"
    )
    code_type: str = Field(
        ...,
        description="Type of dead code (e.g., 'unused function', 'orphan module', 'commented')",
    )
    confidence: ConfidenceLevel = Field(..., description="Confidence level of this finding")
    reason: str = Field(..., description="Why this is considered dead code")
    suggestion: str | None = Field(
        None, description="Suggested action (e.g., 'Remove', 'Investigate further')"
    )
    estimated_lines: int | None = Field(None, description="Estimated number of lines of dead code")


class DeadCodeSummary(BaseModel):
    """Summary statistics for dead code analysis."""

    total_findings: int = Field(..., description="Total number of findings")
    high_confidence_count: int = Field(0, description="Number of high-confidence findings")
    medium_confidence_count: int = Field(0, description="Number of medium-confidence findings")
    low_confidence_count: int = Field(0, description="Number of low-confidence findings")
    estimated_total_lines: int = Field(0, description="Estimated total lines of dead code")


class DeadCodeOutput(BaseCommandOutput):
    """Output schema for 'repodoc deadcode' command."""

    command: str = Field(default="deadcode")
    findings: list[DeadCodeFinding] = Field(
        default_factory=list, description="All dead code findings"
    )
    summary: DeadCodeSummary = Field(..., description="Summary statistics")
    analysis_notes: str | None = Field(
        None, description="Additional notes about the analysis methodology"
    )
