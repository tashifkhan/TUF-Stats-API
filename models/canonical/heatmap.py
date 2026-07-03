from typing import List, Optional

from pydantic import BaseModel, Field


class HeatDay(BaseModel):
    date: str
    count: int
    level: int


class YearContribution(BaseModel):
    year: int
    totalSubmissions: int
    activeDays: int


class Heatmap(BaseModel):
    totalSubmissions: int = 0
    totalActiveDays: int = 0
    currentStreak: int = 0
    longestStreak: int = 0
    maxDailySubmissions: int = 0
    firstActiveDate: Optional[str] = None
    lastActiveDate: Optional[str] = None
    dailyContributions: List[HeatDay] = Field(default_factory=list)
    yearlyContributions: List[YearContribution] = Field(default_factory=list)
    availableYears: List[int] = Field(default_factory=list)
    view: str = "all"
    year: Optional[int] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
