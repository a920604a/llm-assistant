import hashlib
import json
from datetime import timedelta
from typing import Any, Optional

import redis
from api.schemas.ask import AskRequest, AskResponse
from api.schemas.SystemSetting import SystemSettings
from config import RedisPaperSettings, RedisUserSettings
from logger import AppLogger
from services.cache.metrics import monitored_redis

logger = AppLogger(__name__).get_logger()


class CacheClient:
    """Redis-based exact match cache for RAG queries."""

    def __init__(
        self,
        redis_client: redis.Redis,
        settings: RedisUserSettings | RedisPaperSettings,
    ):
        self.redis = redis_client
        self.settings = settings
        self.ttl = timedelta(hours=settings.ttl_hour)

    def _generate_cache_key(self, request: AskRequest) -> str:
        """Generate exact cache key based on request parameters."""
        key_data = {
            "query": request.query,
            "model": request.model,
            "top_k": request.top_k,
            "use_hybrid": request.use_hybrid,
            "categories": sorted(request.categories) if request.categories else [],
        }
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        return f"exact_cache:{key_hash}"

    @monitored_redis
    async def find_cached_response(self, request: AskRequest) -> Optional[AskResponse]:
        """Find cached response for exact query match."""
        try:
            cache_key = self._generate_cache_key(request)

            # Simple Redis GET operation - O(1)
            cached_response = self.redis.get(cache_key)

            if cached_response:
                try:
                    response_data = json.loads(cached_response)
                    logger.info("Cache hit for exact query match")
                    return AskResponse(**response_data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to deserialize cached response: {e}")
                    return None

            return None

        except Exception as e:
            logger.error(f"Error checking cache: {e}")
            return None

    @monitored_redis
    async def store_response(self, request: AskRequest, response: AskResponse) -> bool:
        """Store response for exact query matching."""
        try:
            cache_key = self._generate_cache_key(request)

            # Simple Redis SET operation with TTL
            success = self.redis.set(cache_key, response.model_dump_json(), ex=self.ttl)

            if success:
                logger.info(
                    f"Stored response in exact cache with key {cache_key[:16]}..."
                )
                return True
            else:
                logger.warning("Failed to store response in cache")
                return False

        except Exception as e:
            logger.error(f"Error storing in cache: {e}")
            return False

    @monitored_redis
    def update_redis_system_setting(
        self, user_id: str, systemSettings: SystemSettings
    ) -> None:
        """
        更新 Redis 中的使用者系統設定，每個 field 個別存入 Hash。
        :param user_id: 使用者 ID
        :param settings: SystemSettings instance
        """
        key = f"system_setting:{user_id}"

        # 轉成 dict，並確保都變成 string，方便存入 Redis
        settings_dict = {k: str(v) for k, v in systemSettings.dict().items()}

        # 使用 HMSET (在 redis-py 中是 hset 支援 mapping)
        self.redis.hset(key, mapping=settings_dict)

        # 設定過期時間 (30 天)
        self.redis.expire(key, 3600 * 24 * 30)

        print(f"Updated Redis hash for user {user_id}: {settings_dict}")

    @monitored_redis
    def get_redis_system_setting(self, user_id: str) -> SystemSettings:
        key = f"system_setting:{user_id}"
        data = self.redis.hgetall(key)

        if not data:
            return None  # 或回傳 default

        # Redis 取出的都是 bytes，要 decode 並轉型

        # boolean / int / float 需要轉型
        casted = {
            "user_language": data.get("user_language", "en"),
            "translate": data.get("translate", "False") == "True",
            "system_prompt": data.get("system_prompt", ""),
            "top_k": int(data.get("top_k", "5")),
            "use_rag": data.get("use_rag", "False") == "True",
            "subscribe_email": data.get("subscribe_email", "False") == "True",
            "reranker_enabled": data.get("reranker_enabled", "False") == "True",
            "temperature": float(data.get("temperature", "0.6")),
        }

        return SystemSettings(**casted)

    def update_single_system_setting(
        self, user_id: str, field: str, value: Any
    ) -> None:
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
        self.redis.hset(key, field, str(value))

        # refresh TTL（避免只更新單一欄位時失效）
        self.redis.expire(key, 3600 * 24 * 30)

        print(f"Updated field '{field}' for user {user_id}: {value}")
