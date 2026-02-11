"""Base Pydantic schemas for RepoDoctor."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field


class Severity(StrEnum):
    """Issue severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ConfidenceLevel(StrEnum):
    """Confidence levels for findings."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Issue(BaseModel):
    """Represents a single issue found during analysis."""

    title: str = Field(..., description="Brief title of the issue")
    description: str = Field(..., description="Detailed description of the issue")
    severity: Severity = Field(..., description="Severity level of the issue")
    category: str = Field(..., description="Category or type of issue (e.g., 'bloat', 'security')")
    file_path: str | None = Field(None, description="Path to affected file, if applicable")
    line_number: int | None = Field(None, description="Line number in file, if applicable")
    suggestion: str | None = Field(None, description="Suggested fix or remediation")


class Recommendation(BaseModel):
    """Represents an actionable recommendation."""

    action: str = Field(..., description="Recommended action to take")
    priority: Severity = Field(..., description="Priority level for this recommendation")
    reason: str = Field(..., description="Explanation of why this is recommended")
    estimated_impact: str | None = Field(None, description="Expected impact of the change")


class RepoHealthScore(BaseModel):
    """Repository health score with breakdown."""

    overall_score: Annotated[int, Field(ge=0, le=100)] = Field(
        ..., description="Overall health score (0-100)"
    )
    category_scores: dict[str, Annotated[int, Field(ge=0, le=100)]] = Field(
        default_factory=dict, description="Scores by category (e.g., 'bloat': 85)"
    )
    grade: str = Field(..., description="Letter grade (A, B, C, D, F)")

    @property
    def is_healthy(self) -> bool:
        """Check if repository is considered healthy (score >= 70)."""
        return self.overall_score >= 70


class BaseCommandOutput(BaseModel):
    """Base output schema for all commands."""

    command: str = Field(..., description="Command that produced this output")
    success: bool = Field(True, description="Whether the command completed successfully")
    issues: list[Issue] = Field(default_factory=list, description="Issues found")
    recommendations: list[Recommendation] = Field(
        default_factory=list, description="Actionable recommendations"
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Additional metadata (timestamp, version, etc.)"
    )
