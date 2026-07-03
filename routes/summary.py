from fastapi import APIRouter

from models.canonical import make_envelope
from services import canonical_mapper


router = APIRouter(tags=["Canonical"])


@router.get("/{username}")
async def get_summary(username: str):
    card = await canonical_mapper.build_card(username)
    return make_envelope(username, canonical_mapper.summary_from(card))
