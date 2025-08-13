from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from datetime import date
from typing import Optional
from api.schemas.DashboardStats import DashboardStats
from fastapi import APIRouter, HTTPException, status
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


def verify_firebase_token(authorization: Optional[str] = Header(None)) -> str:
    # logger.info(f"authorization {authorization}")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )
    id_token = authorization.split(" ")[1]
    logger.info(f"id_token {id_token}")

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]
        return user_id
    except Exception as e:
        logger.error(f"Firebase verify_id_token error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/api/dashboard/stats", response_model=DashboardStats)
# async def get_dashboard_stats(user_id: str):
async def get_dashboard_stats(user_id: str = Depends(verify_firebase_token)):

    user_data = fake_db.get("user123")
    if not user_data:
        raise HTTPException(status_code=404, detail="User data not found")

    return DashboardStats(
        uploaded_notes=user_data["uploaded_notes"],
        last_query_date=user_data["last_query_date"],
        total_queries=user_data["total_queries"],
        remaining_tokens=user_data["remaining_tokens"],
    )
