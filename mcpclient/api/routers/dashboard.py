from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from datetime import date
from typing import Optional
from api.schemas.DashboardStats import DashboardStats
from fastapi import APIRouter, HTTPException, status
from api.verify_token import verify_firebase_token
from services.user import get_user_data
import logging

logger = logging.getLogger(__name__)


router = APIRouter()


# 模擬資料庫 (實際應換成你的 DB 查詢)
fake_db = {
    "user123": {
        "uploaded_notes": 32,
        "last_query_date": date(2025, 8, 7),
        "total_queries": 124,
        "remaining_tokens": 1000,
    }
}


@router.get("/api/dashboard/stats", response_model=DashboardStats)
# async def get_dashboard_stats(user_id: str):
async def get_dashboard_stats(user_id: str = Depends(verify_firebase_token)):

    # user_data = fake_db.get("user123")
    user_data = get_user_data(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User data not found")

    return DashboardStats(
        uploaded_notes=user_data["uploaded_notes"],
        last_query_date=user_data["last_query_date"],
        total_queries=user_data["total_queries"],
        remaining_tokens=user_data["remaining_tokens"],
    )
