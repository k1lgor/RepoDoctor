"""Pydantic schemas for RepoDoctor command outputs."""

from repodoc.schemas.base import (
    BaseCommandOutput,
    ConfidenceLevel,
    Issue,
    Recommendation,
    RepoHealthScore,
    Severity,
)
from repodoc.schemas.deadcode import DeadCodeFinding, DeadCodeOutput, DeadCodeSummary
from repodoc.schemas.diet import (
    BloatAnalysis,
    DietOutput,
    DirectoryInfo,
    FileInfo,
    MissingFile,
)
from repodoc.schemas.docker import (
    DockerfileAnalysis,
    DockerIssue,
    DockerOutput,
    PatchedDockerfile,
)
from repodoc.schemas.report import ReportOutput
from repodoc.schemas.scan import ModuleResult, ScanOutput, ScanResult
from repodoc.schemas.tour import (
    DirectoryGuide,
    EntryPoint,
    StackInfo,
    TourOutput,
    TourSummary,
)

__all__ = [
    # Base schemas
    "BaseCommandOutput",
    "Issue",
    "Recommendation",
    "RepoHealthScore",
    "Severity",
    "ConfidenceLevel",
    # Diet
    "DietOutput",
    "BloatAnalysis",
    "FileInfo",
    "DirectoryInfo",
    "MissingFile",
    # Tour
    "TourOutput",
    "TourSummary",
    "StackInfo",
    "EntryPoint",
    "DirectoryGuide",
    # Docker
    "DockerOutput",
    "DockerfileAnalysis",
    "DockerIssue",
    "PatchedDockerfile",
    # Dead Code
    "DeadCodeOutput",
    "DeadCodeFinding",
    "DeadCodeSummary",
    # Scan
    "ScanOutput",
    "ScanResult",
    "ModuleResult",
    # Report
    "ReportOutput",
]
