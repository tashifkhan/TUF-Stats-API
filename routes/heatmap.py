from fastapi import APIRouter, Query

from models.canonical import make_envelope
from services import canonical_mapper
from services.heatmap_window import normalize_view, window_heatmap


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/heatmap")
async def get_heatmap(
    username: str,
    view: str = Query("all", description="all | last_365 | year"),
    year: int | None = Query(None, description="Required when view=year"),
):
    normalized_view, normalized_year = normalize_view(view, year)
    heatmap = await canonical_mapper.build_heatmap(username, normalized_view, normalized_year)
    return make_envelope(username, window_heatmap(heatmap, normalized_view, normalized_year))
