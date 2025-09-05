from config import settings
from logger import AppLogger
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

logger = AppLogger(__name__).get_logger()

# Qdrant client，請確認連線設定
qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    timeout=60,
)  # 總 timeout


# ✅ 建立 Collection（若尚未建立）
def create_qdrant_collection():
    try:
        qdrant_client.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=384, distance=models.Distance.COSINE
            ),
        )
        print(
            f"✅ Qdrant collection `{settings.COLLECTION_NAME}` created successfully."
        )
    except UnexpectedResponse as e:
        # 如果已存在就當作正常，不丟錯
        if "already exists" in str(e):
            logger.info(
                f"ℹ️ Qdrant collection `{settings.COLLECTION_NAME}` already exists, skipping creation."
            )
        else:
            raise  # 其他 UnexpectedResponse 直接丟出
