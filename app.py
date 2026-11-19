from core.runtime import RequestBudgetMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.analytics import AnalyticsMiddleware
from core.middleware import CacheRateLimitMiddleware
from routes.badges import router as badges_router
from routes.contests import router as contests_router
from routes.docs import router as docs_router
from routes.heatmap import router as heatmap_router
from routes.profile import router as profile_router
from routes.rating import router as rating_router
from routes.stats import router as stats_router
from routes.summary import router as summary_router


app = FastAPI(
    title="TUF Stats API",
    version="0.1.0",
    description="FastAPI service for public takeUforward DSA progress statistics.",
)

app.add_middleware(CacheRateLimitMiddleware, platform="tuf")
app.add_middleware(RequestBudgetMiddleware)
# Outside the cache so cache hits and 429s are counted; inside CORS.
app.add_middleware(AnalyticsMiddleware, api="tuf")
# Added last so it is outermost: budget 504s and 429s still carry CORS headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(docs_router)
app.include_router(profile_router)
app.include_router(stats_router)
app.include_router(contests_router)
app.include_router(rating_router)
app.include_router(heatmap_router)
app.include_router(badges_router)
app.include_router(summary_router)
