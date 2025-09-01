# routers/setting.py

from api.metrics import observe_api
from api.schemas.SystemSetting import DEFAULT_SETTINGS, SystemSettings
from api.verify_token import verify_firebase_token  # 解析 Firebase token
from fastapi import APIRouter, Depends
from logger import AppLogger
from services.system_setting import get_setting, post_setting

logger = AppLogger(__name__).get_logger()

router = APIRouter()


@router.get("/api/user/settings", response_model=SystemSettings)
@observe_api
async def get_user_settings(user_id: str = Depends(verify_firebase_token)):
    user_settings = get_setting(user_id)
    return user_settings if user_settings else DEFAULT_SETTINGS


# ---------------------------
# 更新使用者設定
# ---------------------------
@router.post("/api/user/settings", response_model=dict)
@observe_api
async def post_settings(
    settings: SystemSettings, user_id: str = Depends(verify_firebase_token)
):
    return post_setting(user_id, settings)
