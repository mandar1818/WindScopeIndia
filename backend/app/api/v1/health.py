from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def get_health():
    """
    Health check endpoint verifying backend service operation and India Renewable Intelligence status.
    """
    return {
        "status": "healthy",
        "service": "WindScope India — Renewable Energy Intelligence Platform",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform_jurisdiction": "India (28 States & 8 Union Territories)",
        "market_timezone": "Asia/Kolkata (IST)"
    }


