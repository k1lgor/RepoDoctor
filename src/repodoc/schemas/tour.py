"""Schemas for the 'tour' command."""

from pydantic import BaseModel, Field

from repodoc.schemas.base import BaseCommandOutput


class StackInfo(BaseModel):
    """Information about the technology stack."""

    languages: list[str] = Field(default_factory=list, description="Programming languages used")
    frameworks: list[str] = Field(default_factory=list, description="Frameworks detected")
    tools: list[str] = Field(default_factory=list, description="Build tools and package managers")
    databases: list[str] = Field(default_factory=list, description="Databases used, if detectable")


class EntryPoint(BaseModel):
    """Information about a code entry point."""

    file_path: str = Field(..., description="Path to the entry point file")
    description: str = Field(..., description="What this entry point does")
    type: str = Field(..., description="Type of entry point (e.g., 'main', 'server', 'cli')")


class DirectoryGuide(BaseModel):
    """Guide to a directory in the repository."""

    path: str = Field(..., description="Directory path")
    purpose: str = Field(..., description="Purpose of this directory")
    key_files: list[str] = Field(
        default_factory=list, description="Important files in this directory"
    )


class TourSummary(BaseModel):
    """Guided tour summary of the repository."""

    stack: StackInfo = Field(..., description="Technology stack information")
    entry_points: list[EntryPoint] = Field(
        default_factory=list, description="Key entry points to the codebase"
    )
    directory_structure: list[DirectoryGuide] = Field(
        default_factory=list, description="Guide to key directories"
    )
    recommended_reading_order: list[str] = Field(
        default_factory=list, description="Suggested order to read files for onboarding"
    )
    architecture_notes: str | None = Field(None, description="High-level architecture notes")


class TourOutput(BaseCommandOutput):
    """Output schema for 'repodoc tour' command."""

    command: str = Field(default="tour")
    tour: TourSummary = Field(..., description="Guided tour information")
    tour_markdown: str = Field(..., description="Full TOUR.md content as markdown")
