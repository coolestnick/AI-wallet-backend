from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import get_db_session
from app.services.crypto_price import CryptoPriceService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint to verify system status."""
    return {
        "status": "ok",
        "version": "0.1.0-beta",
        "service": "ai-crypto-wallet-backend",
    }


@router.get("/database", status_code=status.HTTP_200_OK)
async def database_health():
    """Check database connection health."""
    try:
        # Try to connect to the database
        with get_db_session() as session:
            # Execute a simple query
            session.execute("SELECT 1")
        return {"database": "connected"}
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )


@router.get("/services", status_code=status.HTTP_200_OK)
async def services_health():
    """Check external services health."""
    health_status = {
        "database": "unknown",
        "crypto_price_service": "unknown",
    }

    # Check database
    try:
        with get_db_session() as session:
            session.execute("SELECT 1")
        health_status["database"] = "healthy"
    except Exception:
        health_status["database"] = "unhealthy"

    # Check crypto price service
    try:
        price_service = CryptoPriceService()
        # Try to get ETH price as a test
        eth_price = price_service.get_token_price(
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH on Ethereum
        )
        health_status["crypto_price_service"] = (
            "healthy" if eth_price is not None else "unhealthy"
        )
    except Exception:
        health_status["crypto_price_service"] = "unhealthy"

    # Determine overall status
    if all(status == "healthy" for status in health_status.values()):
        return {"status": "healthy", "services": health_status}
    else:
        return {"status": "degraded", "services": health_status}
