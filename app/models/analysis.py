from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel


class Analysis(BaseModel):
    """
    Analysis data model.
    This represents a document in the MongoDB Analysis collection.
    """
    id: Optional[str] = None
    slideImage: str
    organ: str
    clinicalContext: str
    model: Literal['JR', 'SR']
    observation: Optional[str] = None
    preliminaryDiagnosis: Optional[str] = None
    confidenceLevel: Optional[str] = None
    disclaimer: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
