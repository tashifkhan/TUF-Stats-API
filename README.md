# TUF Stats API

FastAPI REST API for public takeUforward profile and DSA progress stats.

## Run

```bash
uv sync
uv run python -m uvicorn app:app --reload --port 8007
```

## Canonical Endpoints

```http
GET /{username}
GET /{username}/profile
GET /{username}/stats
GET /{username}/contests
GET /{username}/rating
GET /{username}/heatmap
GET /{username}/badges
```

Heatmap query options:

```http
GET /{username}/heatmap?view=all
GET /{username}/heatmap?view=last_365
GET /{username}/heatmap?view=year&year=2026
```

## Raw Upstream Helpers

```http
GET /raw/{username}/profile
GET /raw/{username}/dsa-progress
GET /raw/{username}/subjects
GET /raw/{username}/heatmap?year=2026
```

The public takeUforward frontend currently uses `https://backend-go.takeuforward.org/api/v1/progress/dsa/{username}` for DSA totals. The older shared-profile URL returns 404 for public username lookup.

The TUF heatmap upstream currently rejects years before 2023, so canonical heatmaps fetch history from 2023 through the current year by default. Override with `TUF_FIRST_HEATMAP_YEAR` if that changes.

## Caching and Rate Limits

The service uses the same Redis-backed middleware pattern as the other Stat APIs.
Set `REDIS_URL` or `TUF_REDIS_URL` to enable response caching, negative user caching,
and per-IP/per-handle rate limits.

Useful env overrides:

```dotenv
TUF_REDIS_URL=redis://localhost:6379/0
TUF_API_CACHE_TTL_SECONDS=3600
TUF_INVALID_USER_CACHE_TTL_SECONDS=300
TUF_RATE_LIMIT_IP_REQUESTS=60
TUF_RATE_LIMIT_HANDLE_REQUESTS=30
```
