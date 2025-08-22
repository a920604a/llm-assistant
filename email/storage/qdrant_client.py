from config import COLLECTION_NAME, QDRANT_URL
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

# Qdrant client，請確認連線設定
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    timeout=60,
)  # 總 timeout


def search():
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
            print(
                f"ℹ️ Qdrant collection `{COLLECTION_NAME}` already exists, skipping creation."
            )
        else:
            raise  # 其他 UnexpectedResponse 直接丟出
