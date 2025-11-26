from typing import Generic, TypeVar, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.mongo import get_database

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    status: bool
    message: str
    data: T


class HistoryItem(BaseModel):
    id: str
    slideImage: str
    organ: str
    clinicalContext: str
    model: str
    observation: Optional[str] = None
    preliminaryDiagnosis: Optional[str] = None
    confidenceLevel: Optional[str] = None
    disclaimer: Optional[str] = None
    createdAt: Optional[str] = None
    feedback: Optional[dict] = None


router = APIRouter(tags=["History"])


@router.get("/history", response_model=ApiResponse[List[HistoryItem]])
async def get_history():
    """
    Retrieve all analysis records with their feedback.
    
    Returns:
        ApiResponse containing a list of all analysis records with feedback field set to null if not present
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database client not initialized")
    
    collection = db["Analysis"]
    
    try:
        documents = []
        async for doc in collection.find():
            history_item = HistoryItem(
                id=str(doc.get("_id")),
                slideImage=doc.get("slideImage", ""),
                organ=doc.get("organ", ""),
                clinicalContext=doc.get("clinicalContext", ""),
                model=doc.get("model", ""),
                observation=doc.get("observation"),
                preliminaryDiagnosis=doc.get("preliminaryDiagnosis"),
                confidenceLevel=doc.get("confidenceLevel"),
                disclaimer=doc.get("disclaimer"),
                createdAt=str(doc.get("createdAt")) if doc.get("createdAt") else None,
                feedback=doc.get("feedback", None)
            )
            documents.append(history_item)
        
        return ApiResponse(
            status=True,
            message="History retrieved successfully",
            data=documents
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database operation failed: {exc}")
