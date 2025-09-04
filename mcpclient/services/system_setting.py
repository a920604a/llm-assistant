import requests
from api.schemas.SystemSetting import DEFAULT_SETTINGS, SystemSettings
from config import NOTE_API_URL
from logger import AppLogger
from redis_client import get_redis_system_setting

logger = AppLogger(__name__).get_logger()


def get_setting(user_id: str) -> SystemSettings:
    _cache = get_redis_system_setting(user_id=user_id)
    return _cache if _cache else DEFAULT_SETTINGS


def post_setting(user_id: str, settings: SystemSettings) -> dict:
    # Update user settings in the database or any other source
    payload = {"user_id": user_id, "new_settings": settings.dict()}
    resp = requests.post(f"{NOTE_API_URL}/api/settings", json=payload, timeout=5)
    if resp.status_code == 200:
        return {"status": True, "message": "Settings updated successfully"}
    else:
        return {"status": False, "message": "Failed to update settings"}
