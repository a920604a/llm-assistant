from api.schemas.SystemSetting import SystemSettings, DEFAULT_SETTINGS
import requests
from conf import NOTE_API_URL
from logger import get_logger
from redis_client import get_redis_system_setting


logger = get_logger(__name__)


def get_setting(user_id: str) -> SystemSettings:
    _cache = get_redis_system_setting(user_id=user_id)
    return _cache if _cache else DEFAULT_SETTINGS
    # Retrieve user settings from the database or any other source
    # resp = requests.get(f"{NOTE_API_URL}/api/setting", params={"user_id": user_id})
    # if resp.status_code == 200:
    #     logger.info(f"resp {resp.json()}")
    #     data = resp.json()
    #     return data

    # return DEFAULT_SETTINGS


def post_setting(user_id: str, settings: SystemSettings) -> dict:
    # Update user settings in the database or any other source
    payload = {"user_id": user_id, "new_settings": settings.dict()}
    resp = requests.post(
        f"{NOTE_API_URL}/api/settings",
        json=payload,
    )
    if resp.status_code == 200:
        return {"status": True, "message": "Settings updated successfully"}
    else:
        return {"status": False, "message": "Failed to update settings"}
