from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
from datetime import datetime
from src.backend.ai.prompts.prompt import AUDITOR_AGENT_PROMPT
from src.backend.core.config import settings

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

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

# ============================================================================
# MOCK DATABASE & MONGODB FUNCTIONS
# ============================================================================

def mock_get_audit_rules() -> List[dict]:
    """
    Mock function to get audit rules from database.
    Replace this with actual database call later.
    """
    return [
        {
            "rule_id": "R001",
            "rule_name": "Insured Name Validation",
            "rule_description": "Insured name must not be empty and should have valid characters",
            "severity": "critical"
        },
        {
            "rule_id": "R002",
            "rule_name": "Date Range Validation",
            "rule_description": "Effective date must be before expiry date",
            "severity": "critical"
        },
        {
            "rule_id": "R003",
            "rule_name": "Sum Insured Validation",
            "rule_description": "Total sum insured must be greater than zero",
            "severity": "high"
        },
        {
            "rule_id": "R004",
            "rule_name": "Underwriter Assignment",
            "rule_description": "Submission must have an assigned underwriter",
            "severity": "critical"
        },
        {
            "rule_id": "R005",
            "rule_name": "Line of Business Validation",
            "rule_description": "Line of business must be selected from predefined list",
            "severity": "high"
        },
        {
            "rule_id": "R006",
            "rule_name": "Documentation Completeness",
            "rule_description": "All required documents must be attached and verified",
            "severity": "high"
        },
        {
            "rule_id": "R007",
            "rule_name": "Broker Validation",
            "rule_description": "Broker must be registered in the system",
            "severity": "medium"
        },
        {
            "rule_id": "R008",
            "rule_name": "Risk Assessment",
            "rule_description": "Risk factors must be documented and assessed",
            "severity": "high"
        }
    ]



def mock_get_context_from_mongodb(submission_id: str, query: str) -> str:
    """
    Mock function to retrieve context from MongoDB vector store.
    Replace this with actual MongoDB vector search call later.
    
    Args:
        submission_id: The submission to retrieve context for
        query: The query to search for in vector store
    
    Returns:
        Retrieved context/documents as string
    """
    # Mock response based on submission_id and query
    mock_contexts = {
        "documentation": """
        Documents found in submission:
        - Policy Details: Complete with all coverages listed
        - Insured Information: Full details provided
        - Risk Assessment Report: Comprehensive assessment included
        - Broker Authorization: Valid and signed
        - Claims History: No recent claims found
        """,
        "risk_assessment": """
        Risk Assessment Details:
        - Risk Level: Medium
        - Industry Type: Manufacturing
        - Location Risk: Standard
        - Previous Claims: None in last 5 years
        - Underwriting Notes: Favorable risk profile
        """,
        "compliance": """
        Compliance Check Results:
        - KYC Status: Verified
        - AML Check: Passed
        - Regulatory Status: Compliant
        - Documentation: All required documents submitted
        """,
        "financial": """
        Financial Information:
        - Sum Insured: $500,000
        - Premium Amount: $25,000
        - Payment Terms: Quarterly
        - Financial Rating: A+
        """
    }
    
    # Return appropriate mock context
    for key, context in mock_contexts.items():
        if key in query.lower():
            return context
    
    return """
    General Context Retrieved:
    - Submission Status: Draft
    - Submission Date: 2026-01-13
    - Underwriting Year: 2026
    - Policy Type: Commercial General Liability
    """

# ============================================================================
# AUDITOR AGENT CLASS
# ============================================================================

class AuditorAgent:
    """AI-powered auditor agent for validating submissions against rules"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuditorAgent, cls).__new__(cls)
            cls._instance.__initialize_agent()
        return cls._instance
    
    def __initialize_agent(self):
        """Initialize the auditor agent with LLM"""
        model_name = "qwen2.5-coder"
        model_provider = "ollama"
        base_url = "https://waldo-unappliable-supersolemnly.ngrok-free.dev"
        api_key = settings.model_api_key.get_secret_value()
        
        self.model = init_chat_model(
            model=model_name,
            model_provider=model_provider,
            base_url=base_url,
            api_key=api_key
        )
        
        print("Auditor Agent initialized")
    
    def _get_audit_rules(self) -> List[dict]:
        """Retrieve audit rules from database (mocked)"""
        return mock_get_audit_rules()
    
    def _retrieve_context(self, submission_id: str, rule: dict) -> str:
        """Retrieve relevant context from MongoDB (mocked)"""
        query = f"submission:{submission_id} context:document {rule.get('rule_name', '')}"
        return mock_get_context_from_mongodb(submission_id, query)
    
    async def evaluate_submission(
        self,
        submission_id: str
    ) -> AuditResponse:
        """
        Evaluate a submission against all audit rules in PARALLEL for faster execution
        
        Args:
            submission_id: The submission ID to audit
        
        Returns:
            AuditResponse with detailed validation results
        """
        # Get audit rules
        rules = self._get_audit_rules()
        
        # Create tasks for all rules to run in parallel
        tasks = [
            self._evaluate_single_rule(submission_id, rule)
            for rule in rules
        ]

        # Execute all evaluations concurrently
        validation_results = await asyncio.gather(*tasks)
        
        # Calculate pass/fail counts
        passed_count = sum(1 for r in validation_results if r.status.upper() == "PASS")
        failed_count = len(validation_results) - passed_count
        
        # Determine overall status
        overall_status = "PASS" if failed_count == 0 else "FAIL"
        
        # Create audit response
        audit_response = AuditResponse(
            submission_id=submission_id,
            overall_status=overall_status,
            evaluated_at=datetime.now(),
            total_rules=len(rules),
            passed_rules=passed_count,
            failed_rules=failed_count,
            validation_results=validation_results
        )
        
        return audit_response
    
    async def _evaluate_single_rule(
        self,
        submission_id: str,
        rule: dict
    ) -> RuleValidationResult:
        """
        Evaluate a single rule (called in parallel for all rules)
        
        Args:
            submission_id: The submission ID
            rule: The rule to evaluate
        
        Returns:
            RuleValidationResult for this specific rule
        """
        # Retrieve context for this rule
        doc_context = self._retrieve_context(submission_id, rule)
        
        prompt = AUDITOR_AGENT_PROMPT.format(
            context=doc_context,
            rule_id=rule["rule_id"],
            rule_name=rule["rule_name"],
            rule_description=rule["rule_description"],
            severity=rule["severity"]
        )

        response =  await self.model.ainvoke(prompt)

        # Parse and return result
        return self._parse_evaluation_response(
            rule_id=rule['rule_id'],
            rule_name=rule['rule_name'],
            rule_description=rule['rule_description'],
            response_text=response.content
        )
    
    def _format_submission_data(self, submission_data: dict) -> str:
        """Format submission data for prompt"""
        lines = []
        for key, value in submission_data.items():
            if value is not None:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def _parse_evaluation_response(
        self,
        rule_id: str,
        rule_name: str,
        rule_description: str,
        response_text: str
    ) -> RuleValidationResult:
        """Parse LLM response into structured result"""
        
        # Extract status
        status = "FAIL"  # Default
        if "Status: PASS" in response_text or "status: pass" in response_text.lower():
            status = "PASS"
        elif "Status: FAIL" in response_text or "status: fail" in response_text.lower():
            status = "FAIL"
        
        # Extract evidence
        evidence = ""
        if "Evidence:" in response_text:
            evidence = response_text.split("Evidence:")[1].split("\n")[0].strip()
        
        # Extract details
        details = ""
        if "Details:" in response_text:
            details = response_text.split("Details:")[1].strip()
        
        # Fallback if parsing fails
        if not evidence:
            evidence = response_text[:200] if response_text else "No evidence provided"
        if not details:
            details = response_text[200:500] if len(response_text) > 200 else response_text
        
        return RuleValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            rule_description=rule_description,
            status=status,
            evidence=evidence,
            details=details
        )

# Singleton instance
auditor_agent = AuditorAgent()
