# routers/setting.py

from api.auto_metrics import observe_api
from api.schemas.SystemSetting import DEFAULT_SETTINGS, SystemSettings
from api.verify_token import verify_firebase_token  # 解析 Firebase token
from core.limiter import limiter
from fastapi import APIRouter, Depends, Request
from logger import AppLogger
from services.system_setting import get_setting, post_setting

logger = AppLogger(__name__).get_logger()

router = APIRouter()


@router.get("/api/user/settings", response_model=SystemSettings)
@limiter.limit("5/minute")  # 每分鐘 5 次
@observe_api
async def get_user_settings(
    request: Request, user_id: str = Depends(verify_firebase_token)
):
    user_settings = get_setting(user_id)
    return user_settings if user_settings else DEFAULT_SETTINGS


# ---------------------------
# 更新使用者設定
# ---------------------------
@router.post("/api/user/settings", response_model=dict)
@limiter.limit("10/minute")  # 每分鐘 5 次
@observe_api
async def post_settings(
    request: Request,
    settings: SystemSettings,
    user_id: str = Depends(verify_firebase_token),
):
    return post_setting(user_id, settings)
