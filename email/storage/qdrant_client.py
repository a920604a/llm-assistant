from typing import Optional

from config import COLLECTION_NAME, QDRANT_URL
from qdrant_client import QdrantClient, models
from services.embedding import get_embedding

# Qdrant client，請確認連線設定
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    timeout=300,
)  # 總 timeout


def fetch_paper_content_from_qdrant(
    arxiv_id: Optional[str] = None,
    title: Optional[str] = None,
    abstract: Optional[str] = None,
    top_k: int = 1,
) -> str:
    """
    從 Qdrant 使用混合搜尋抓取 raw_content：
    - metadata filter: arxiv_id 或 title
    - embedding search: 使用 abstract/title embedding
    """
    must_conditions = []
    if arxiv_id:
        must_conditions.append(
            models.FieldCondition(
                key="arxiv_id",
                match=models.MatchValue(value=arxiv_id),
            )
        )
    if title:
        must_conditions.append(
            models.FieldCondition(
                key="title",
                match=models.MatchValue(value=title),
            )
        )
    metadata_filter = models.Filter(must=must_conditions) if must_conditions else None

    # 計算 embedding
    text_for_embedding = title or "" + (abstract or "")
    query_vector = get_embedding(text_for_embedding) if text_for_embedding else None

    if query_vector:
        search_result = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            filter=metadata_filter,
            with_payload=True,
        )
    else:
        # fallback to scroll if no embedding
        search_result, _ = qdrant_client.scroll(
            collection_name=COLLECTION_NAME, scroll_filter=metadata_filter, limit=top_k
        )

    if not search_result:
        return ""

    payload = search_result[0].payload
    return payload.get("raw_content", "")
