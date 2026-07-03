from datetime import datetime, timezone

from fastapi import APIRouter

from services.client import fetch_dsa_progress, fetch_heatmap_year, fetch_profile, fetch_subjects_progress


router = APIRouter(prefix="/raw", tags=["Raw"])


@router.get("/{username}/profile")
async def raw_profile(username: str):
    return await fetch_profile(username)


@router.get("/{username}/dsa-progress")
async def raw_dsa_progress(username: str):
    return await fetch_dsa_progress(username)


@router.get("/{username}/subjects")
async def raw_subjects(username: str):
    return await fetch_subjects_progress(username)


@router.get("/{username}/heatmap")
async def raw_heatmap(username: str, year: int | None = None):
    selected_year = year or datetime.now(timezone.utc).year
    return await fetch_heatmap_year(username, selected_year)
