import re
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, EmailStr

class VendorInfo(BaseModel):
    name: str
    tax_id: str = Field(..., description="Tax ID in format XX-000-0000")
    email: str = Field(..., description="Contact email for the vendor")

    @field_validator("tax_id")
    @classmethod
    def validate_tax_id(cls, v: str) -> str:
        if not re.match(r"^[A-Z]{2}-\d{3}-\d{4}$", v):
            raise ValueError("Tax ID must follow format: XX-000-0000 (e.g., US-123-4567)")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v

class InvoiceItem(BaseModel):
    description: str
    category: Literal["Hardware", "Software", "Service", "Other"]
    quantity: int
    unit_price: float
    total: float
    is_taxable: bool = True
    math_reasoning: str = Field(..., description="Explain the calculation")

    @model_validator(mode="after")
    def validate_item_total(self) -> "InvoiceItem":
        expected_total = self.quantity * self.unit_price
        if abs(self.total - expected_total) > 0.01:
            raise ValueError(f"Math Error in '{self.description}': {self.quantity} x {self.unit_price} is {expected_total}, not {self.total}")
        return self

class StructuredOutput(BaseModel):
    """Extreme complexity model with math, tax, vendor validation, and temporal logic."""
    model_config = ConfigDict(extra="forbid")

    project_name: str
    vendor: VendorInfo
    start_date: str
    end_date: str
    items: List[InvoiceItem]
    tax_rate: float = Field(..., description="Tax rate as a decimal (e.g., 0.08 for 8%)")
    tax_amount: float = Field(..., description="Total tax calculated on taxable items")
    discount_amount: float = Field(default=0.0, description="Any flat discount applied BEFORE tax")
    grand_total: float = Field(..., description="Final amount after tax and discounts")
    correction_notes: Optional[str] = None

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
            raise ValueError(f"End date ({self.end_date}) is before start date ({self.start_date})")
        return self

    @model_validator(mode="after")
    def validate_financials(self) -> "StructuredOutput":
        # 1. Calculate taxable and subtotal
        subtotal = sum(item.total for item in self.items)
        taxable_subtotal = sum(item.total for item in self.items if item.is_taxable)
        
        # 2. Check Tax amount
        # Formula: (Taxable Subtotal - Discount) * Rate 
        # (Assuming discount is applied proportionally or to subtotal specifically)
        # We'll stick to a simpler: (Taxable Subtotal) * Rate
        expected_tax = taxable_subtotal * self.tax_rate
        if abs(self.tax_amount - expected_tax) > 0.05:
            raise ValueError(f"Tax Mismatch: Taxable subtotal is {taxable_subtotal}, at rate {self.tax_rate}, tax should be {expected_tax}, not {self.tax_amount}")
        
        # 3. Check Grand Total
        # Formula: Subtotal - Discount + Tax
        expected_grand = subtotal - self.discount_amount + self.tax_amount
        if abs(self.grand_total - expected_grand) > 0.05:
            raise ValueError(f"Grand Total Mismatch: Subtotal({subtotal}) - Discount({self.discount_amount}) + Tax({self.tax_amount}) should be {expected_grand}, not {self.grand_total}")
        
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
