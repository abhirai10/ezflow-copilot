from typing import Optional, List
from src.backend.services.sql_service import DatabaseManager
from src.backend.schemas.submission import SubmissionCreate, SubmissionUpdate

class SubmissionService:
    """Service layer for submission CRUD operations"""
    
    def __init__(self):
        self.db = DatabaseManager.get_shared_db()
    
    async def create_submission(self, submission: SubmissionCreate) -> dict:
        """Create a new submission"""
        query = f"""
        INSERT INTO Submissions (
            SubmissionNo, InsuredName, BrokerName, CedantName, Department,
            ProfitCenter, LineOfBusiness, TotalSumInsured, EffectiveDate, ExpiryDate,
            OverAllStatus, Underwriter, TechnicalAssistant, UnderwritingYear, CreatedBy
        )
        VALUES (
            '{submission.submission_no}', 
            '{submission.insured_name}', 
            '{submission.broker_name}', 
            '{submission.cedant_name}', 
            '{submission.department}',
            '{submission.profit_center}', 
            '{submission.line_of_business}', 
            {submission.total_sum_insured or 'NULL'}, 
            '{submission.effective_date or 'NULL'}', 
            '{submission.expiry_date or 'NULL'}',
            '{submission.overall_status}', 
            '{submission.underwriter}', 
            '{submission.technical_assistant}', 
            {submission.underwriting_year or 'NULL'}, 
            '{submission.created_by}'
        )
        """
        try:
            self.db.run(query)
            return {"message": "Submission created successfully", "submission_no": submission.submission_no}
        except Exception as e:
            raise Exception(f"Error creating submission: {str(e)}")
    
    async def get_submission(self, submission_id: str) -> dict:
        """Get a specific submission by ID"""
        query = f"SELECT * FROM Submissions WHERE SubmissionID = '{submission_id}'"
        try:
            result = self.db.run(query)
            return result if result else {"error": "Submission not found"}
        except Exception as e:
            raise Exception(f"Error fetching submission: {str(e)}")
    
    async def get_submission_by_no(self, submission_no: str) -> dict:
        """Get a specific submission by SubmissionNo"""
        query = f"SELECT * FROM Submissions WHERE SubmissionNo = '{submission_no}'"
        try:
            result = self.db.run(query)
            return result if result else {"error": "Submission not found"}
        except Exception as e:
            raise Exception(f"Error fetching submission: {str(e)}")
    
    async def get_all_submissions(
        self, 
        insured_name: Optional[str] = None,
        overall_status: Optional[str] = None,
        underwriter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """Get all submissions with optional filters"""
        filters = []
        
        if insured_name:
            filters.append(f"InsuredName LIKE '%{insured_name}%'")
        if overall_status:
            filters.append(f"OverAllStatus = '{overall_status}'")
        if underwriter:
            filters.append(f"Underwriter = '{underwriter}'")
        
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        
        query = f"""
        SELECT * FROM Submissions {where_clause}
        ORDER BY CreatedAt DESC
        OFFSET {skip} ROWS
        FETCH NEXT {limit} ROWS ONLY
        """
        
        try:
            result = self.db.run(query)
            return result if result else []
        except Exception as e:
            raise Exception(f"Error fetching submissions: {str(e)}")
    
    async def update_submission(self, submission_id: str, submission: SubmissionUpdate) -> dict:
        """Update a submission"""
        updates = []
        
        if submission.submission_no is not None:
            updates.append(f"SubmissionNo = '{submission.submission_no}'")
        if submission.insured_name is not None:
            updates.append(f"InsuredName = '{submission.insured_name}'")
        if submission.broker_name is not None:
            updates.append(f"BrokerName = '{submission.broker_name}'")
        if submission.cedant_name is not None:
            updates.append(f"CedantName = '{submission.cedant_name}'")
        if submission.department is not None:
            updates.append(f"Department = '{submission.department}'")
        if submission.profit_center is not None:
            updates.append(f"ProfitCenter = '{submission.profit_center}'")
        if submission.line_of_business is not None:
            updates.append(f"LineOfBusiness = '{submission.line_of_business}'")
        if submission.total_sum_insured is not None:
            updates.append(f"TotalSumInsured = {submission.total_sum_insured}")
        if submission.effective_date is not None:
            updates.append(f"EffectiveDate = '{submission.effective_date}'")
        if submission.expiry_date is not None:
            updates.append(f"ExpiryDate = '{submission.expiry_date}'")
        if submission.overall_status is not None:
            updates.append(f"OverAllStatus = '{submission.overall_status}'")
        if submission.underwriter is not None:
            updates.append(f"Underwriter = '{submission.underwriter}'")
        if submission.technical_assistant is not None:
            updates.append(f"TechnicalAssistant = '{submission.technical_assistant}'")
        if submission.underwriting_year is not None:
            updates.append(f"UnderwritingYear = {submission.underwriting_year}")
        
        updates.append("UpdatedAt = CURRENT_TIMESTAMP")
        
        if len(updates) <= 1:  # Only UpdatedAt was added
            return {"message": "No updates provided"}
        
        update_clause = ", ".join(updates)
        query = f"UPDATE Submissions SET {update_clause} WHERE SubmissionID = '{submission_id}'"
        
        try:
            self.db.run(query)
            return {"message": "Submission updated successfully", "submission_id": submission_id}
        except Exception as e:
            raise Exception(f"Error updating submission: {str(e)}")
    
    async def delete_submission(self, submission_id: str) -> dict:
        """Delete a submission"""
        query = f"DELETE FROM Submissions WHERE SubmissionID = '{submission_id}'"
        
        try:
            self.db.run(query)
            return {"message": "Submission deleted successfully", "submission_id": submission_id}
        except Exception as e:
            raise Exception(f"Error deleting submission: {str(e)}")

