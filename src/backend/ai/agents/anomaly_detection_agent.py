from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List
import asyncio
from datetime import datetime
from src.backend.core.config import settings

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class DetectedAnomaly(BaseModel):
    """A detected anomaly in submission documents"""
    anomaly_id: str
    document_type: str
    anomaly_type: str  # e.g., "missing_field", "inconsistent_data", "suspicious_pattern"
    severity: str = Field(..., description="low, medium, high, critical")
    description: str
    affected_field: str
    evidence: str
    recommended_action: str

class AnomalyDetectionResponse(BaseModel):
    """Complete anomaly detection response"""
    submission_id: str
    documents_analyzed: int
    anomalies_detected: int
    risk_level: str = Field(..., description="low, medium, high, critical")
    detected_anomalies: List[DetectedAnomaly]
    summary: str
    analyzed_at: datetime

# ============================================================================
# MOCK DATABASE & MONGODB FUNCTIONS
# ============================================================================

def mock_get_submission_documents(submission_id: str) -> List[dict]:
    """
    Mock function to retrieve submission documents from MongoDB.
    Replace this with actual MongoDB call later.
    """
    return [
        {
            "document_id": "DOC001",
            "document_type": "Policy_Details",
            "content": "Policy Number: POL-2026-001\nEffective Date: 2026-01-01\nExpiry Date: 2027-01-01\nPremium: $25,000",
            "uploaded_date": "2026-01-10",
            "file_size": 1024
        },
        {
            "document_id": "DOC002",
            "document_type": "Insured_Information",
            "content": "Company Name: ABC Manufacturing\nRegistration No: REG-12345\nIndustry: Manufacturing\nEmployees: 250",
            "uploaded_date": "2026-01-10",
            "file_size": 512
        },
        {
            "document_id": "DOC003",
            "document_type": "Risk_Assessment",
            "content": "Risk Level: Medium\nLocation: Industrial Area\nPrevious Claims: None\nAssessment Date: 2025-12-15",
            "uploaded_date": "2026-01-08",
            "file_size": 2048
        },
        {
            "document_id": "DOC004",
            "document_type": "Financial_Statements",
            "content": "Revenue: $5,000,000\nProfit: $500,000\nYear: 2025",
            "uploaded_date": "2026-01-09",
            "file_size": 1536
        },
        {
            "document_id": "DOC005",
            "document_type": "Broker_Authorization",
            "content": "Broker: XYZ Insurance Brokers\nAuthorization: Valid\nExpiry: 2027-06-30",
            "uploaded_date": "2026-01-10",
            "file_size": 768
        }
    ]

def mock_get_document_metadata(document_id: str) -> dict:
    """
    Mock function to retrieve detailed metadata for a document.
    Replace this with actual database call later.
    """
    metadata_db = {
        "DOC001": {
            "validation_status": "valid",
            "last_modified": "2026-01-10",
            "version": "1.0",
            "checksum": "abc123def456"
        },
        "DOC002": {
            "validation_status": "valid",
            "last_modified": "2026-01-10",
            "version": "2.0",
            "checksum": "xyz789abc456"
        },
        "DOC003": {
            "validation_status": "valid",
            "last_modified": "2026-01-08",
            "version": "1.0",
            "checksum": "def456ghi789"
        },
        "DOC004": {
            "validation_status": "valid",
            "last_modified": "2026-01-09",
            "version": "1.0",
            "checksum": "ghi789jkl012"
        },
        "DOC005": {
            "validation_status": "valid",
            "last_modified": "2026-01-10",
            "version": "1.0",
            "checksum": "jkl012mno345"
        }
    }
    
    return metadata_db.get(document_id, {
        "validation_status": "unknown",
        "last_modified": "unknown",
        "version": "unknown",
        "checksum": "unknown"
    })

# ============================================================================
# ANOMALY DETECTION AGENT CLASS
# ============================================================================

class AnomalyDetectionAgent:
    """AI-powered agent for detecting anomalies in submission documents"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnomalyDetectionAgent, cls).__new__(cls)
            cls._instance.__initialize_agent()
        return cls._instance
    
    def __initialize_agent(self):
        """Initialize the anomaly detection agent with LLM"""
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
        
        print("Anomaly Detection Agent initialized")
    
    def _get_submission_documents(self, submission_id: str) -> List[dict]:
        """Retrieve submission documents from MongoDB (mocked)"""
        return mock_get_submission_documents(submission_id)
    
    def _get_document_metadata(self, document_id: str) -> dict:
        """Retrieve document metadata from database (mocked)"""
        return mock_get_document_metadata(document_id)
    
    async def detect_anomalies(self, submission_id: str) -> AnomalyDetectionResponse:
        """
        Detect anomalies in submission documents
        
        Args:
            submission_id: The submission ID to analyze
        
        Returns:
            AnomalyDetectionResponse with detected anomalies
        """
        
        # Get all submission documents
        documents = self._get_submission_documents(submission_id)
        
        # Create tasks to analyze each document in parallel
        tasks = [
            self._analyze_document(submission_id, doc)
            for doc in documents
        ]
        
        # Execute all analyses concurrently
        analysis_results = await asyncio.gather(*tasks)
        
        # Flatten and collect all detected anomalies
        all_anomalies = []
        for result in analysis_results:
            all_anomalies.extend(result)
        
        # Determine overall risk level
        risk_levels = ["low", "medium", "high", "critical"]
        max_severity_index = 0
        
        for anomaly in all_anomalies:
            try:
                severity_index = risk_levels.index(anomaly.severity)
                max_severity_index = max(max_severity_index, severity_index)
            except ValueError:
                pass
        
        overall_risk_level = risk_levels[max_severity_index] if all_anomalies else "low"
        
        # Create summary
        if all_anomalies:
            critical_count = sum(1 for a in all_anomalies if a.severity == "critical")
            high_count = sum(1 for a in all_anomalies if a.severity == "high")
            summary = f"Found {len(all_anomalies)} anomalies: {critical_count} critical, {high_count} high priority items detected."
        else:
            summary = "No anomalies detected in submission documents."
        
        # Create response
        anomaly_response = AnomalyDetectionResponse(
            submission_id=submission_id,
            documents_analyzed=len(documents),
            anomalies_detected=len(all_anomalies),
            risk_level=overall_risk_level,
            detected_anomalies=all_anomalies,
            summary=summary,
            analyzed_at=datetime.now()
        )
        
        return anomaly_response
    
    async def _analyze_document(self, submission_id: str, document: dict) -> List[DetectedAnomaly]:
        """
        Analyze a single document for anomalies (called in parallel for all documents)
        
        Args:
            submission_id: The submission ID
            document: The document to analyze
        
        Returns:
            List of DetectedAnomaly objects for this document
        """
        
        # Get document metadata
        metadata = self._get_document_metadata(document.get("document_id"))
        
        # Build analysis prompt
        prompt = f"""
        You are an expert document analyst specializing in detecting anomalies and inconsistencies in insurance submissions.
        
        DOCUMENT DETAILS:
        Document ID: {document.get('document_id')}
        Document Type: {document.get('document_type')}
        Uploaded Date: {document.get('uploaded_date')}
        File Size: {document.get('file_size')} bytes
        
        DOCUMENT CONTENT:
        {document.get('content')}
        
        DOCUMENT METADATA:
        {self._format_metadata(metadata)}
        
        TASK:
        Analyze this document for potential anomalies, inconsistencies, missing information, or suspicious patterns.
        Check for:
        1. Missing required fields or data
        2. Inconsistent or conflicting information
        3. Unusual patterns or values
        4. Data quality issues
        5. Outdated information
        
        For EACH anomaly found, provide:
        - Anomaly Type (missing_field, inconsistent_data, suspicious_pattern, data_quality, outdated_info)
        - Severity (low, medium, high, critical)
        - Affected Field: [field name]
        - Evidence: [specific evidence from document]
        - Recommended Action: [what should be done]
        
        If no anomalies found, respond with: "NO_ANOMALIES_FOUND"
        """
        
        # Get LLM analysis
        response_text = await self.model.ainvoke(prompt)
        
        # Parse response into DetectedAnomaly objects
        return self._parse_anomaly_response(
            document_id=document.get("document_id"),
            document_type=document.get("document_type"),
            response_text=response_text
        )
    
    def _format_metadata(self, metadata: dict) -> str:
        """Format metadata for prompt"""
        lines = []
        for key, value in metadata.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines) if lines else "No metadata available"
    
    def _parse_anomaly_response(
        self,
        document_id: str,
        document_type: str,
        response_text: str
    ) -> List[DetectedAnomaly]:
        """Parse LLM response into DetectedAnomaly objects"""
        
        anomalies = []
        
        # Check if no anomalies found
        if "NO_ANOMALIES_FOUND" in response_text:
            return anomalies
        
        # Parse each anomaly from response
        # Split by numbered items or anomaly markers
        lines = response_text.split("\n")
        current_anomaly = {}
        anomaly_counter = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a new anomaly
            if "Anomaly Type:" in line or "anomaly type:" in line.lower():
                if current_anomaly:
                    # Save previous anomaly
                    anomaly = self._create_anomaly(document_id, document_type, current_anomaly, anomaly_counter)
                    if anomaly:
                        anomalies.append(anomaly)
                        anomaly_counter += 1
                
                current_anomaly = {}
                anomaly_type = line.split(":")[-1].strip()
                current_anomaly["anomaly_type"] = anomaly_type
            
            elif "Severity:" in line or "severity:" in line.lower():
                severity = line.split(":")[-1].strip().lower()
                current_anomaly["severity"] = severity
            
            elif "Affected Field:" in line or "affected field:" in line.lower():
                field = line.split(":")[-1].strip()
                current_anomaly["affected_field"] = field
            
            elif "Evidence:" in line or "evidence:" in line.lower():
                evidence = line.split(":")[-1].strip()
                current_anomaly["evidence"] = evidence
            
            elif "Recommended Action:" in line or "recommended action:" in line.lower():
                action = line.split(":")[-1].strip()
                current_anomaly["recommended_action"] = action
        
        # Add last anomaly
        if current_anomaly:
            anomaly = self._create_anomaly(document_id, document_type, current_anomaly, anomaly_counter)
            if anomaly:
                anomalies.append(anomaly)
        
        return anomalies
    
    def _create_anomaly(
        self,
        document_id: str,
        document_type: str,
        anomaly_data: dict,
        counter: int
    ) -> DetectedAnomaly:
        """Create a DetectedAnomaly object from parsed data"""
        
        try:
            return DetectedAnomaly(
                anomaly_id=f"{document_id}-ANOM{counter}",
                document_type=document_type,
                anomaly_type=anomaly_data.get("anomaly_type", "unknown"),
                severity=anomaly_data.get("severity", "medium"),
                description=f"{anomaly_data.get('anomaly_type', 'Unknown')} detected in {document_type}",
                affected_field=anomaly_data.get("affected_field", "N/A"),
                evidence=anomaly_data.get("evidence", "No evidence provided"),
                recommended_action=anomaly_data.get("recommended_action", "Review document")
            )
        except Exception:
            return None

# Singleton instance
anomaly_detection_agent = AnomalyDetectionAgent()
