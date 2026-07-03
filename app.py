from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.middleware import CacheRateLimitMiddleware
from routes.badges import router as badges_router
from routes.contests import router as contests_router
from routes.docs import router as docs_router
from routes.heatmap import router as heatmap_router
from routes.profile import router as profile_router
from routes.rating import router as rating_router
from routes.raw import router as raw_router
from routes.stats import router as stats_router
from routes.summary import router as summary_router


app = FastAPI(
    title="TUF Stats API",
    version="0.1.0",
    description="FastAPI service for public takeUforward DSA progress statistics.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CacheRateLimitMiddleware, platform="tuf")

app.include_router(docs_router)
app.include_router(raw_router)
app.include_router(profile_router)
app.include_router(stats_router)
app.include_router(contests_router)
app.include_router(rating_router)
app.include_router(heatmap_router)
app.include_router(badges_router)
app.include_router(summary_router)
