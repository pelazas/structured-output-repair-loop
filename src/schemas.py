from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class StructuredOutput(BaseModel):
    """Model for structured data extraction results."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="The name of the entity or subject")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    action_items: List[str] = Field(default_factory=list, description="A list of specific follow-up tasks")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format (e.g., 2024-01-01)")
        return v

    @field_validator("action_items")
    @classmethod
    def validate_action_items(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Action items list cannot be empty")
        for item in v:
            if not item.strip():
                raise ValueError("Action items cannot contain empty strings")
        return v

class ExtractorState(BaseModel):
    """Model representing the state of the extraction process."""
    model_config = ConfigDict(extra="forbid")

    raw_text: str = Field(default="", description="The original input text")
    current_attempt: int = Field(default=0, description="The current step or iteration index")
    validation_errors: List[str] = Field(default_factory=list, description="List of error messages from last validation")
    attempt_count: int = Field(default=0, description="Total number of attempts made")
    final_output: Optional[StructuredOutput] = Field(default=None, description="The final validated output")
    is_valid: bool = Field(default=False, description="Whether the current extraction is valid")
    warning_flag: bool = Field(default=False, description="Indicates if any non-critical warnings were triggered")
