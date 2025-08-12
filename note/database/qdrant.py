from qdrant_client import QdrantClient, models 



# Qdrant client，請確認連線設定
qdrant_client = QdrantClient(host="qdrant", port=6333)