from typing import Optional
from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    """
    Feedback request model.
    """
    rating: int
    notes: str


class FeedbackResponse(BaseModel):
    """
    Feedback response model.
    """
    id: Optional[str] = None
    rating: int
    notes: str
