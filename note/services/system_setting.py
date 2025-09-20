# services/system_setting.py
from typing import Optional

from api.schemas.SystemSetting import PostSettingsRequest, SystemSettings
from db.crud.setting import get, update
from logger import AppLogger
from services.cache.client import CacheClient

logger = AppLogger(__name__).get_logger()


def get_setting(user_id: str) -> Optional[SystemSettings]:
    setting = get(user_id)
    logger.info(f"Retrieved settings for user {user_id}: {setting}")
    if setting:
        return SystemSettings(**setting)
    else:
        return None


def post_setting(req: PostSettingsRequest, user_cache_client: CacheClient) -> bool:
    logger.info(f"Updating settings for user {req.user_id}: {req.new_settings.dict()}")
    # save to redis
    user_cache_client.update_redis_system_setting(req.user_id, req.new_settings)
    # save to db
    return update(req.user_id, req.new_settings.dict(exclude_unset=True))
