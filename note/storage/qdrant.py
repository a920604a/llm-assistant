from qdrant_client import QdrantClient, models 
from conf import QDRANT_URL


# Qdrant client，請確認連線設定
qdrant_client = QdrantClient(url=QDRANT_URL)