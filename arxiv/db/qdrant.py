from config import COLLECTION_NAME, QDRANT_URL
from logger import get_logger
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

logger = get_logger(__name__)


# Qdrant client，請確認連線設定
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    timeout=300,
)  # 總 timeout


# ✅ 建立 Collection（若尚未建立）
def create_qdrant_collection():
    try:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=768, distance=models.Distance.COSINE
            ),
        )
        print(f"✅ Qdrant collection `{COLLECTION_NAME}` created successfully.")
    except UnexpectedResponse as e:
        # 如果已存在就當作正常，不丟錯
        if "already exists" in str(e):
            logger.info(
                f"ℹ️ Qdrant collection `{COLLECTION_NAME}` already exists, skipping creation."
            )
        else:
            raise  # 其他 UnexpectedResponse 直接丟出
