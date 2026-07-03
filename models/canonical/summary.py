from typing import Optional

from pydantic import BaseModel


class Summary(BaseModel):
    totalSolved: int = 0
    totalActiveDays: int = 0
    totalContests: int = 0
    currentRating: Optional[int] = None
    maxRating: Optional[int] = None
    rank: Optional[str] = None
    badgesCount: int = 0
