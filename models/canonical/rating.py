from typing import List, Optional

from pydantic import BaseModel, Field


class RatingPoint(BaseModel):
    timestamp: Optional[int] = None
    rating: Optional[int] = None
    contestName: Optional[str] = None


class Rating(BaseModel):
    current: Optional[int] = None
    max: Optional[int] = None
    history: List[RatingPoint] = Field(default_factory=list)
