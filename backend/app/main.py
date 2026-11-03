from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.api.v1.router import api_v1_router
from app.api.v1.health import router as health_router

app = FastAPI(
    title="WindScope India — Renewable Energy Intelligence Platform",
    description=(
        "Enterprise analytics platform for Indian renewable energy intelligence. "
        "Provides multi-year (2020-2026), all-India coverage across all 28 States and 8 Union Territories "
        "for Wind, Solar, Large Hydro, Small Hydro, and Biomass generation from official CEA and NPP sources, "
        "with interactive choropleth mapping, 15-minute forecasting accuracy, and regional grid council analytics."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://.*windscope.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
# Also include /health directly at root for Docker/K8s probes
app.include_router(health_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "WindScope India — Renewable Energy Intelligence Platform",
        "version": "2.1.0",
        "status": "operational",
        "documentation": "/docs",
        "platform_scope": "Multi-Year Indian Renewable Energy (2020-2026)",
        "jurisdiction": "28 States & 8 Union Territories",
        "grid_timezone": "Asia/Kolkata (IST)",
        "api_v1": settings.API_V1_PREFIX,
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request.",
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

