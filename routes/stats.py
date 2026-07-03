from fastapi import APIRouter

from models.canonical import make_envelope
from services import canonical_mapper
from services.client import fetch_dsa_progress, fetch_subjects_progress


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/stats")
async def get_stats(username: str):
    progress_payload = await fetch_dsa_progress(username)
    subjects_payload = await fetch_subjects_progress(username)
    return make_envelope(
        username,
        canonical_mapper.stats_from(progress_payload, subjects_payload),
        legacy=progress_payload,
    )
