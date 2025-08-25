from arxiv_ingestion.config import QDRANT_URL
from logger import get_logger
from qdrant_client import QdrantClient

logger = get_logger(__name__)


# Qdrant client，請確認連線設定
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    timeout=60,
)  # 總 timeout
