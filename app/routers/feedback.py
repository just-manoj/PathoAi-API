from typing import Generic, TypeVar
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from bson import ObjectId
from app.db.mongo import get_database
from app.models.feedback import FeedbackRequest, FeedbackResponse

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    status: bool
    message: str
    data: T

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=ApiResponse[FeedbackResponse])
async def submit_feedback(
    id: str = Query(..., description="Analysis document ID"),
    feedback: FeedbackRequest = None
):
    """
    Submit feedback for an analysis.
    
    Args:
        id: Analysis document ID (query parameter)
        feedback: FeedbackRequest containing rating and notes (request body)
    
    Returns:
        ApiResponse containing the feedback data inserted into Analysis collection entry
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database client not initialized")
    
    collection = db["Analysis"]
    
    try:
        analysis_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid analysis ID format")
    
    try:
        result = await collection.update_one(
            {"_id": analysis_id},
            {
                "$set": {
                    "feedback": {
                        "rating": feedback.rating,
                        "notes": feedback.notes
                    }
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return ApiResponse(
            status=True,
            message="Feedback submitted successfully",
            data=FeedbackResponse(
                id=id,
                rating=feedback.rating,
                notes=feedback.notes
            )
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database operation failed: {exc}")
