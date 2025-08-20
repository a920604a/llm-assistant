import redis
from typing import Any
from conf import REDIS_URL
from api.schemas.SystemSetting import SystemSettings

redis_client = redis.from_url(REDIS_URL, decode_responses=True)  # 回傳字串


def update_redis_system_setting(user_id: str, settings: SystemSettings) -> None:
    """
    更新 Redis 中的使用者系統設定，每個 field 個別存入 Hash。
    :param user_id: 使用者 ID
    :param settings: SystemSettings instance
    """
    key = f"system_setting:{user_id}"

    # 轉成 dict，並確保都變成 string，方便存入 Redis
    settings_dict = {k: str(v) for k, v in settings.dict().items()}

    # 使用 HMSET (在 redis-py 中是 hset 支援 mapping)
    redis_client.hset(key, mapping=settings_dict)

    # 設定過期時間 (30 天)
    redis_client.expire(key, 3600 * 24 * 30)

    print(f"Updated Redis hash for user {user_id}: {settings_dict}")


# HGETALL system_setting:123
# {
#   "user_language": "zh-TW",
#   "translate": "True",
#   "system_prompt": "你是助手",
#   "top_k": "5",
#   "use_rag": "True",
#   "subscribe_email": "False",
#   "reranker_enabled": "True",
#   "temperature": "0.7"
# }


def get_redis_system_setting(user_id: str) -> SystemSettings:
    key = f"system_setting:{user_id}"
    data = redis_client.hgetall(key)

    if not data:
        return None  # 或回傳 default

    # Redis 取出的都是 bytes，要 decode 並轉型
    decoded = {k.decode(): v.decode() for k, v in data.items()}

    # boolean / int / float 需要轉型
    casted = {
        "user_language": decoded.get("user_language", "en"),
        "translate": decoded.get("translate", "False") == "True",
        "system_prompt": decoded.get("system_prompt", ""),
        "top_k": int(decoded.get("top_k", "5")),
        "use_rag": decoded.get("use_rag", "False") == "True",
        "subscribe_email": decoded.get("subscribe_email", "False") == "True",
        "reranker_enabled": decoded.get("reranker_enabled", "False") == "True",
        "temperature": float(decoded.get("temperature", "0.6")),
    }

    return SystemSettings(**casted)


def update_single_system_setting(user_id: str, field: str, value: Any) -> None:
    """
    更新 Redis 中的單一使用者系統設定 field。
    :param user_id: 使用者 ID
    :param field: 欲更新的欄位名稱 (需存在於 SystemSettings)
    :param value: 欲更新的值
    """
    key = f"system_setting:{user_id}"

    # 檢查欄位是否存在於 SystemSettings
    if field not in SystemSettings.__fields__:
        raise ValueError(f"Invalid field: {field}")

    # 轉成字串存 Redis（避免型別問題）
    redis_client.hset(key, field, str(value))

    # refresh TTL（避免只更新單一欄位時失效）
    redis_client.expire(key, 3600 * 24 * 30)

    print(f"Updated field '{field}' for user {user_id}: {value}")
