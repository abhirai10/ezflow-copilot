from fastapi import APIRouter, HTTPException
from src.backend.ai.agents.auditor_agent import auditor_agent, AuditResponse
from src.backend.ai.agents.anomaly_detection_agent import anomaly_detection_agent, AnomalyDetectionResponse

router = APIRouter()

@router.post("/audit/{submission_id}", response_model=AuditResponse)
async def audit_submission(submission_id: str, submission_data: dict):
    """
    Evaluate a submission against all audit rules.
    
    Args:
        submission_id: The ID of the submission to audit
        submission_data: Dictionary containing submission details
    
    Returns:
        AuditResponse with detailed validation results for each rule
    """
    try:
        # Evaluate the submission
        audit_result = await auditor_agent.evaluate_submission(
            submission_id=submission_id,
            submission_data=submission_data
        )
        
        return audit_result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during audit evaluation: {str(e)}"
        )

@router.post("/anomalies/{submission_id}", response_model=AnomalyDetectionResponse)
async def detect_document_anomalies(submission_id: str):
    """
    Detect anomalies in submission documents.
    
    Args:
        submission_id: The ID of the submission to analyze
    
    Returns:
        AnomalyDetectionResponse with detected anomalies and risk assessment
    """
    try:
        # Detect anomalies in documents
        anomaly_result = await anomaly_detection_agent.detect_anomalies(
            submission_id=submission_id
        )
        
        return anomaly_result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during anomaly detection: {str(e)}"
        )
