from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
import logging

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Music Streaming API",
    description="Backend for the Music Streaming Application — search, stream, recommendations, and user activity.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting Music Streaming API...")

    try:
        from app.firebase.firebase_init import initialize_firebase
        ok = initialize_firebase()
        if not ok:
            logger.warning("⚠️  Running without Firebase — auth/activity endpoints will fail")
    except Exception as e:
        logger.error(f"❌ Firebase init error: {e}")

    logger.info("✅ Startup complete")


# ── Register Routes ─────────────────────────────────────────────────────────
try:
    from app.routes import auth, search, songs, recommendations, activity, preferences, metadata, podcasts

    app.include_router(auth.router,            prefix="/auth",       tags=["Auth"])
    app.include_router(search.router,                                tags=["Search"])
    app.include_router(songs.router,                                 tags=["Music"])
    app.include_router(recommendations.router,                       tags=["Recommendations"])
    app.include_router(activity.router,         prefix="/user",      tags=["Activity"])
    app.include_router(preferences.router,      prefix="/user",      tags=["User"])
    app.include_router(metadata.router,         prefix="/metadata",  tags=["Metadata"])
    app.include_router(podcasts.router,                                tags=["Podcasts"])

    logger.info("✅ All routes loaded")
except Exception as e:
    logger.error(f"❌ Route loading failed: {e}", exc_info=True)


# ── Health & Info ───────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": "Music Streaming API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}
