"""Schemas for the 'diet' command."""

from pydantic import BaseModel, Field

from repodoc.schemas.base import BaseCommandOutput


class FileInfo(BaseModel):
    """Information about a file."""

    path: str = Field(..., description="Relative path to the file")
    size_bytes: int = Field(..., description="File size in bytes")
    size_human: str = Field(..., description="Human-readable size (e.g., '1.5 MB')")


class DirectoryInfo(BaseModel):
    """Information about a directory."""

    path: str = Field(..., description="Relative path to the directory")
    size_bytes: int = Field(..., description="Total size in bytes")
    size_human: str = Field(..., description="Human-readable size (e.g., '150 MB')")
    file_count: int = Field(..., description="Number of files in directory")


class MissingFile(BaseModel):
    """Information about a missing hygiene file."""

    filename: str = Field(..., description="Name of the missing file")
    importance: str = Field(..., description="Why this file is important")
    template_url: str | None = Field(None, description="URL to a template, if available")


class BloatAnalysis(BaseModel):
    """Repository bloat and hygiene analysis results."""

    total_size_bytes: int = Field(..., description="Total repository size in bytes")
    total_size_human: str = Field(..., description="Human-readable total size")
    largest_files: list[FileInfo] = Field(
        default_factory=list, description="Top largest files (typically top 10)"
    )
    largest_directories: list[DirectoryInfo] = Field(
        default_factory=list, description="Top largest directories (typically top 10)"
    )
    suspected_artifacts: list[str] = Field(
        default_factory=list,
        description="Paths to suspected build artifacts or unnecessary files",
    )
    missing_hygiene_files: list[MissingFile] = Field(
        default_factory=list, description="Standard files that are missing"
    )


class DietOutput(BaseCommandOutput):
    """Output schema for 'repodoc diet' command."""

    command: str = Field(default="diet")
    analysis: BloatAnalysis = Field(..., description="Bloat analysis results")
    diet_markdown: str = Field(..., description="Full DIET.md content as markdown")
