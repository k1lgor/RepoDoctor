"""Schemas for the 'report' command."""

from pydantic import BaseModel, ConfigDict, Field


class ReportOutput(BaseModel):
    """Output schema for 'repodoc report' command."""

    model_config = ConfigDict(extra="allow")  # Allow extra fields like issues, recommendations

    command: str = Field(default="report")
    success: bool = Field(default=True)
    markdown_content: str = Field(..., description="Generated Markdown report")
    report_title: str = Field(..., description="Title of the report")
    generation_timestamp: str = Field(..., description="When the report was generated")
