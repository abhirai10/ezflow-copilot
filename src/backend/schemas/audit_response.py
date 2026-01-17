from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

class RuleValidationResult(BaseModel):
    """Result of validating a single rule"""
    rule_id: str = Field(..., description="Rule Id")
    rule_name: str = Field(..., description="Rule Name")
    rule_description: str = Field(..., description="Rule Description")
    status: str = Field(..., description="Pass or Fail")
    evidence: str = Field(..., description="Evidence or reason for the status")
    details: str = Field(..., description="Detailed findings against this rule")

class AuditResponse(BaseModel):
    """Complete audit response for a submission"""
    submission_id: str
    overall_status: str = Field(..., description="Overall Pass or Fail")
    evaluated_at: datetime
    total_rules: int
    passed_rules: int
    failed_rules: int
    validation_results: List[RuleValidationResult]



