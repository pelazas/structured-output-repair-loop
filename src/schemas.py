from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class InvoiceItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

    @model_validator(mode="after")
    def validate_item_total(self) -> "InvoiceItem":
        expected_total = self.quantity * self.unit_price
        if abs(self.total - expected_total) > 0.01:
            raise ValueError(f"Total for '{self.description}' must be {expected_total}, but got {self.total}")
        return self

class StructuredOutput(BaseModel):
    """Model for advanced structured data extraction with math and temporal logic."""
    model_config = ConfigDict(extra="forbid")

    project_name: str = Field(..., description="The name of the project")
    start_date: str = Field(..., description="Project start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Project end date (YYYY-MM-DD)")
    items: List[InvoiceItem] = Field(..., description="List of invoiced items")
    grand_total: float = Field(..., description="The sum of all item totals")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    @model_validator(mode="after")
    def validate_temporal_logic(self) -> "StructuredOutput":
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")
        if end < start:
            raise ValueError(f"End date ({self.end_date}) cannot be before start date ({self.start_date})")
        return self

    @model_validator(mode="after")
    def validate_grand_total(self) -> "StructuredOutput":
        calculated_total = sum(item.total for item in self.items)
        if abs(self.grand_total - calculated_total) > 0.01:
            raise ValueError(f"Grand total must be {calculated_total}, but got {self.grand_total}")
        return self

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
