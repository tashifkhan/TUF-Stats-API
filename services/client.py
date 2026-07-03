import os
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException


BASE_URL = os.getenv("TUF_BACKEND_URL", "https://backend-go.takeuforward.org/api").rstrip("/")
TIMEOUT = float(os.getenv("TUF_REQUEST_TIMEOUT", "20"))

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://takeuforward.org",
    "referer": "https://takeuforward.org/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": os.getenv(
        "TUF_USER_AGENT",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:152.0) Gecko/20100101 Firefox/152.0",
    ),
}


def _message(payload: Any, fallback: str) -> str:
    if isinstance(payload, dict):
        for key in ("message", "error", "detail"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return fallback


async def fetch_json(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
            response = await client.get(url, params=params)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="TUF upstream request timed out") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"TUF upstream request failed: {exc}") from exc

    try:
        payload = response.json() if response.content else {}
    except ValueError:
        payload = {}
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=_message(payload, f"HTTP {response.status_code}"))
    if isinstance(payload, dict) and payload.get("success") is False:
        raise HTTPException(status_code=502, detail=_message(payload, "TUF upstream returned an error"))
    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail="TUF upstream returned invalid JSON")
    return payload


async def fetch_profile(username: str) -> Dict[str, Any]:
    return await fetch_json(f"v1/shared/profile/get-profile/{username}")


async def fetch_dsa_progress(username: str) -> Dict[str, Any]:
    return await fetch_json(f"v1/progress/dsa/{username}")


async def fetch_subjects_progress(username: str) -> Dict[str, Any]:
    return await fetch_json(f"v1/progress/subjects/{username}")


async def fetch_heatmap_year(username: str, year: int) -> Dict[str, Any]:
    return await fetch_json(f"v1/streak/heatmap/{username}", {"year": year})
