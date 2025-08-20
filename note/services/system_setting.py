# services/system_setting.py
from api.schemas.SystemSetting import SystemSettings, DEFAULT_SETTINGS
from storage.crud.setting import get, update
from typing import Optional
from logger import get_logger


logger = get_logger(__name__)


def get_setting(user_id: str) -> Optional[SystemSettings]:
    setting = get(user_id)
    logger.info(f"Retrieved settings for user {user_id}: {setting}")
    if setting:
        return SystemSettings(**setting)
    else:
        return None


def post_setting(user_id: str, settings: SystemSettings) -> bool:
    logger.info(f"Updating settings for user {user_id}: {settings.dict()}")
    return update(user_id, settings.dict(exclude_unset=True))
