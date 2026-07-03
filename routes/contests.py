from fastapi import APIRouter

from models.canonical import Contests, make_envelope
from services.client import fetch_dsa_progress


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/contests")
async def get_contests(username: str):
    await fetch_dsa_progress(username)
    return make_envelope(username, Contests())
