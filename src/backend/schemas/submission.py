from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from uuid import UUID

class SubmissionBase(BaseModel):
    submission_no: str
    insured_name: str
    broker_name: Optional[str] = None
    cedant_name: Optional[str] = None
    department: Optional[str] = None
    profit_center: Optional[str] = None
    line_of_business: Optional[str] = None
    total_sum_insured: Optional[float] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    overall_status: str = "Draft"
    underwriter: Optional[str] = None
    technical_assistant: Optional[str] = None
    underwriting_year: Optional[int] = None
    created_by: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionUpdate(BaseModel):
    submission_no: Optional[str] = None
    insured_name: Optional[str] = None
    broker_name: Optional[str] = None
    cedant_name: Optional[str] = None
    department: Optional[str] = None
    profit_center: Optional[str] = None
    line_of_business: Optional[str] = None
    total_sum_insured: Optional[float] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    overall_status: Optional[str] = None
    underwriter: Optional[str] = None
    technical_assistant: Optional[str] = None
    underwriting_year: Optional[int] = None

class SubmissionResponse(SubmissionBase):
    submission_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

