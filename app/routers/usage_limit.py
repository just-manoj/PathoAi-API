from typing import List, Generic, TypeVar, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from app.db.mongo import get_database
from app.models.usage_limit import UsageLimit

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    status: bool
    message: str
    data: T

router = APIRouter(prefix="/modelLimit", tags=["UsageLimit"])


@router.get("", response_model=ApiResponse[UsageLimit])
async def get_today_usage_limit():
    """
    Get today's usage limit record from the database.
    
    Returns:
        ApiResponse containing today's UsageLimit document from MongoDB
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database client not initialized")

    collection = db["UsageLimit"]
    today_str = date.today().strftime("%d-%m-%Y")

    try:
        # Correct date filter
        doc = await collection.find_one({"date": today_str})

        if not doc:
            raise HTTPException(404, detail="No usage found for today's date")

        doc["id"] = str(doc["_id"])
        usage = UsageLimit(**doc)

        return ApiResponse(
            status=True,
            message="Usage limit retrieved successfully",
            data=usage
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database query failed: {exc}"
        )


