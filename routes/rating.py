from fastapi import APIRouter

from models.canonical import Rating, make_envelope
from services.client import fetch_dsa_progress


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/rating")
async def get_rating(username: str):
    await fetch_dsa_progress(username)
    return make_envelope(username, Rating())
