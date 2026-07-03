from fastapi import APIRouter

from models.canonical import make_envelope
from services import canonical_mapper
from services.client import fetch_profile


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/profile")
async def get_profile(username: str):
    profile_payload = await fetch_profile(username)
    return make_envelope(username, canonical_mapper.profile_from(profile_payload, username), legacy=profile_payload)
