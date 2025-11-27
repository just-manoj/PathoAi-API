from datetime import date
from typing import Optional
from pydantic import BaseModel


class UsageLimit(BaseModel):
    """
    Usage limit data model.
    This represents a document in the MongoDB UsageLimit collection.
    """
    id: Optional[str] = None  # MongoDB _id (shown as 'id' in API)
    date: str
    jrUsed: int
    srUsed: int
    jrLimit: int
    srLimit: int

    class Config:
        populate_by_name = True  # Allow '_id' or 'id' in input


