from langchain.chat_models import init_chat_model
import asyncio
from datetime import datetime
from src.backend.ai.prompts.prompt import AUDITOR_AGENT_PROMPT
from src.backend.core.config import settings
from src.backend.schemas.audit_response import AuditResponse, RuleValidationResult
from src.backend.services.auditor_service import get_audit_rules_from_db
from src.backend.services.mongo_vectorstore_service import get_document_context


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
    
    
    async def _retrieve_context(self, submission_id: str, rule: dict) -> str:
        """Retrieve relevant context from MongoDB (mocked)"""
        query = f"submission:{submission_id} context:document {rule.get('rule_name', '')}"
        return await get_document_context(submission_id, query)
    
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
        rules = get_audit_rules_from_db()
        
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
        doc_context = await self._retrieve_context(submission_id, rule)

        # 2. Format the context with Source names
        formatted_context = ""
        for i, doc in enumerate(doc_context):
            source = doc.metadata.get('FileName', 'Unknown Source')
            formatted_context += f"\n--- Source {i+1}: {source} ---\n{doc.page_content}\n"
        
        prompt = AUDITOR_AGENT_PROMPT.format(
            context=formatted_context,
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
