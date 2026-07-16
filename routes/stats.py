from fastapi import APIRouter, Query

from models.canonical import make_envelope
from services import canonical_mapper
from services.client import fetch_dsa_progress, fetch_subjects_progress
from services.stats_svg import stats_svg_response


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/stats/svg", summary="Stats SVG card")
async def get_stats_svg(
    username: str,
    theme: str = Query("dark", description="Card theme: dark or light"),
):
    progress_payload = await fetch_dsa_progress(username)
    subjects_payload = await fetch_subjects_progress(username)
    data = canonical_mapper.stats_from(progress_payload, subjects_payload)
    return stats_svg_response("tuf", username, data, theme=theme)


@router.get("/{username}/stats")
async def get_stats(username: str):
    progress_payload = await fetch_dsa_progress(username)
    subjects_payload = await fetch_subjects_progress(username)
    return make_envelope(
        username,
        canonical_mapper.stats_from(progress_payload, subjects_payload),
        legacy=progress_payload,
    )
