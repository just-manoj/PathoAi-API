from typing import List, Generic, TypeVar, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.mongo import get_database
from app.models.usage_limit import UsageLimit

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    status: bool
    message: str
    data: T

router = APIRouter(prefix="/modelLimit", tags=["UsageLimit"])


@router.get("", response_model=ApiResponse[List[UsageLimit]])
async def get_all_usage_limits():
    """
    Get all usage limit records from the database.
    
    Returns:
        ApiResponse containing list of all UsageLimit documents from MongoDB
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database client not initialized")
    collection = db["UsageLimit"]
    results = []
    try:
        async for doc in collection.find({}):
            print("Getting all usage limits",doc)
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
            results.append(UsageLimit(**doc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database query failed: {exc}")

    return ApiResponse(status=True, message="Usage limits retrieved successfully", data=results)


