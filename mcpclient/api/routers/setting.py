# routers/setting.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from api.verify_token import verify_firebase_token  # 解析 Firebase token
from services.system_setting import get_setting, post_setting

from api.schemas.SystemSetting import SystemSettings, DEFAULT_SETTINGS
from logger import get_logger


logger = get_logger(__name__)

router = APIRouter()


@router.get("/api/user/settings", response_model=SystemSettings)
# async def get_user_settings(user_id: str = Depends(verify_firebase_token)):
async def get_user_settings(user_id: str):
    # user_settings = get_user_data(user_id).get("settings")
    # if not user_settings:
    #     logger.info(f"User {user_id} uses default settings")
    #     return DEFAULT_SETTINGS
    # logger.info(f"User {user_id} settings retrieved: {user_settings}")
    # return SystemSettings(**user_settings)
    user_settings = get_setting(user_id)
    return user_settings if user_settings else DEFAULT_SETTINGS


# ---------------------------
# 更新使用者設定
# ---------------------------
@router.post("/api/user/settings", response_model=dict)
# async def put_settings(
#     settings: SystemSettings, user_id: str = Depends(verify_firebase_token)
# ):
async def post_settings(settings: SystemSettings, user_id: str):
    # success = update_user_settings(user_id, settings.dict())
    # if not success:
    #     raise HTTPException(status_code=500, detail="Failed to update settings")
    # logger.info(f"User {user_id} settings updated: {settings.dict()}")

    return post_setting(user_id, settings)
