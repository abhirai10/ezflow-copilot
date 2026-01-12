from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from src.backend.schemas.submission import SubmissionCreate, SubmissionUpdate
from src.backend.services.submission_service import SubmissionService

router = APIRouter()
submission_service = SubmissionService()

# CREATE
@router.post("/", response_model=dict, status_code=201)
async def create_submission(submission: SubmissionCreate):
    """Create a new submission"""
    try:
        result = await submission_service.create_submission(submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# READ - Get all submissions with filters
@router.get("/", response_model=List[dict])
async def list_submissions(
    insured_name: Optional[str] = Query(None),
    overall_status: Optional[str] = Query(None),
    underwriter: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all submissions with optional filters"""
    try:
        result = await submission_service.get_all_submissions(
            insured_name=insured_name,
            overall_status=overall_status,
            underwriter=underwriter,
            skip=skip,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# READ - Get submission by ID
@router.get("/{submission_id}", response_model=dict)
async def get_submission(submission_id: str):
    """Get a specific submission by ID"""
    try:
        result = await submission_service.get_submission(submission_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# READ - Get submission by SubmissionNo
@router.get("/number/{submission_no}", response_model=dict)
async def get_submission_by_number(submission_no: str):
    """Get a specific submission by SubmissionNo"""
    try:
        result = await submission_service.get_submission_by_no(submission_no)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# UPDATE
@router.put("/{submission_id}", response_model=dict)
async def update_submission(submission_id: str, submission: SubmissionUpdate):
    """Update a submission"""
    try:
        result = await submission_service.update_submission(submission_id, submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# DELETE
@router.delete("/{submission_id}", response_model=dict)
async def delete_submission(submission_id: str):
    """Delete a submission"""
    try:
        result = await submission_service.delete_submission(submission_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



