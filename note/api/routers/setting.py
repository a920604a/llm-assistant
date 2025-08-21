# routers/setting.py
from api.schemas.SystemSetting import (
    DEFAULT_SETTINGS,
    PostSettingsRequest,
    SystemSettings,
)
from fastapi import APIRouter
from logger import get_logger
from services.system_setting import get_setting, post_setting

logger = get_logger(__name__)

router = APIRouter()


@router.get("/api/setting", response_model=SystemSettings)
async def get_user_settings(user_id: str):
    user_settings = get_setting(user_id)
    logger.info("get_user_settings %s", user_settings)
    return SystemSettings(**user_settings) if user_settings else DEFAULT_SETTINGS


# ---------------------------
# 更新使用者設定
# ---------------------------


@router.post("/api/settings", response_model=dict)
async def post_settings(req: PostSettingsRequest):
    logger.info("post_settings %s", req)
    post_setting(req.user_id, req.new_settings)
    return {"status": True, "message": "Settings updated successfully"}
