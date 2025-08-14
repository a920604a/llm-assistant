from qdrant_client import QdrantClient, models
from conf import QDRANT_URL, COLLECTION_NAME


# Qdrant client，請確認連線設定
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    timeout=60,  # 總 timeout
)


# # ✅ 建立 Collection（若尚未建立）
# def create_qdrant_collection():
#     try:
#         qdrant_client.create_collection(
#             collection_name=COLLECTION_NAME,
#             vectors_config=models.VectorParams(
#                 size=384, distance=models.Distance.COSINE
#             ),
#             exist_ok=True,  # collection 已存在就忽略
#         )
#     except Exception as e:
#         print(f"建立 collection 發生錯誤: {e}")
