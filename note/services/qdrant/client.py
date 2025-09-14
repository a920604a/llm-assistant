from typing import Dict, List, Optional

from config import Settings
from logger import AppLogger
from qdrant_client import QdrantClient as Client
from qdrant_client import models
from qdrant_client.http.exceptions import UnexpectedResponse

logger = AppLogger(__name__).get_logger()


class QdrantClient:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.client = Client(
            url=settings.QDRANT_URL,
            timeout=60,
        )

    def create_collection(self):
        try:
            self.client.create_collection(
                collection_name=self.settings.COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=768, distance=models.Distance.COSINE
                ),
            )
            print(
                f"✅ Qdrant collection `{self.settings.COLLECTION_NAME}` created successfully."
            )
        except UnexpectedResponse as e:
            # 如果已存在就當作正常，不丟錯
            if "already exists" in str(e):
                logger.info(
                    f"ℹ️ Qdrant collection `{self.settings.COLLECTION_NAME}` already exists, skipping creation."
                )
            else:
                raise  # 其他 UnexpectedResponse 直接丟出

    def get_collections(self):
        return self.client.get_collections()

    def search_native(
        self,
        size: int = 10,
        query_vector: Optional[List[float]] = None,
    ):
        return self.client.search(
            collection_name=self.settings.COLLECTION_NAME,
            query_vector=query_vector,
            limit=size,
            with_payload=True,
        )

    def search(
        self,
        query: str,
        query_vector: Optional[List[float]] = None,
        size: int = 10,
        categories: Optional[List[str]] = None,
        min_score: float = 0.25,
    ) -> tuple[List[Dict], List[str], str, List[str], int]:
        # Step 1: 建立 Qdrant filter
        must_conditions = []

        if categories:
            must_conditions.append(
                models.FieldCondition(
                    key="categories", match=models.MatchValue(value=categories)
                )
            )

        filter_cond = models.Filter(must=must_conditions) if must_conditions else None

        logger.info(f"filter_cond {filter_cond}")
        # Step 2: Qdrant search
        # Hybrid search：向量 + filter
        query_result = self.client.search(
            collection_name=self.settings.COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=filter_cond,
            limit=size,
            with_payload=True,
        )

        # Extract essential data for LLM
        chunks = []
        arxiv_ids = []
        sources = set()

        # [ScoredPoint(id=2952, version=30, score=0.591295, payload= {'arxiv_id' : XXX, 'abstract': XXX, 'title': XXX, 'authors': XXX, 'categories': XXX, 'published_date': XXX, 'text': XXX, 'chunk_idx': XXX}
        msg = ""
        for hit in query_result:
            if hit.score < min_score:
                continue
            payload = hit.payload
            arxiv_id = payload.get("arxiv_id", "")

            # Minimal chunk data for LLM
            chunks.append(
                {
                    "arxiv_id": arxiv_id,
                    "chunk_text": payload.get("text", payload.get("abstract", "")),
                }
            )

            if arxiv_id:
                arxiv_ids.append(arxiv_id)
                arxiv_id_clean = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id
                sources.add(f"https://arxiv.org/pdf/{arxiv_id_clean}.pdf")

            info_str = f"title: {payload['title']} \n Score: {hit.score}\n arxiv_id : {payload['arxiv_id']}"
            msg += f"Retrieved {len(chunks)} chunks from collection {self.settings.COLLECTION_NAME}\n{info_str}\n\n\n"

        return chunks, list(sources), msg, arxiv_ids, len(query_result)
