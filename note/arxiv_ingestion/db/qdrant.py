from config import settings
from logger import AppLogger
from qdrant_client import QdrantClient

logger = AppLogger(__name__).get_logger()


# Qdrant client，請確認連線設定
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    timeout=60,
)  # 總 timeout
