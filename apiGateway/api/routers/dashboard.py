from datetime import date

from api.auto_metrics import observe_api
from api.schemas.DashboardStats import DashboardStats
from api.verify_token import verify_firebase_token
from core.limiter import limiter
from fastapi import APIRouter, Depends, HTTPException, Request
from logger import AppLogger
from services.user import get_user_data

logger = AppLogger(__name__).get_logger()


router = APIRouter()


# 模擬資料庫 (實際應換成你的 DB 查詢)
fake_db = {
    "user123": {
        "uploaded_papers": 32,
        "last_query_date": date(2025, 8, 7),
        "total_queries": 124,
        "remaining_tokens": 1000,
    }
}


@router.get("/api/v1/dashboard/stats", response_model=DashboardStats)
@limiter.limit("20/minute")  # 每分鐘 20 次
@observe_api
# async def get_dashboard_stats(user_id: str):
async def get_dashboard_stats(
    request: Request, user_id: str = Depends(verify_firebase_token)
):
    # user_data = fake_db.get("user123")

    user_data = get_user_data(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User data not found")

    logger.info(f"User {user_id} dashboard stats retrieved: {user_data}")

    return DashboardStats(
        uploaded_papers=user_data["uploaded_papers"],
        last_query_date=user_data["last_query_date"],
        total_queries=user_data["total_queries"],
        remaining_tokens=user_data["remaining_tokens"],
    )
