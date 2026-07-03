from fastapi import APIRouter

from models.canonical import Badges, make_envelope
from services.client import fetch_dsa_progress


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/badges")
async def get_badges(username: str):
    await fetch_dsa_progress(username)
    return make_envelope(username, Badges())
