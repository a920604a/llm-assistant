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
                vectors_config={
                    "dense": models.VectorParams(
                        size=768,
                        distance=models.Distance.COSINE,
                    ),
                },
                sparse_vectors_config={
                    "bm25": models.SparseVectorParams(
                        modifier=models.Modifier.IDF,
                    )
                },
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
        query: str,
        size: int = 10,
        query_vector: Optional[List[float]] = None,
        hybrid_search: bool = False,
    ):
        if hybrid_search:
            query_result = self.client.query_points(
                collection_name=self.settings.COLLECTION_NAME,
                prefetch=[
                    models.Prefetch(query=query_vector, using="dense", limit=5 * size),
                    models.Prefetch(
                        query=models.Document(
                            text=query,
                            model="Qdrant/bm25",
                        ),
                        using="bm25",
                        limit=5 * size,
                    ),
                ],
                # Fusion query enables fusion on the prefetched results
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=size,
                with_payload=True,
            )
        else:
            logger.info("Dense-only search")
            # 🚀 Dense-only search
            query_result = self.client.query_points(
                collection_name=self.settings.COLLECTION_NAME,
                query=query_vector,
                using="dense",
                limit=size,
                with_payload=True,
            )
        return query_result.points

    def search(
        self,
        query: str,
        query_vector: Optional[List[float]] = None,
        size: int = 10,
        categories: Optional[List[str]] = None,
        min_score: float = 0.25,
        hybrid: bool = True,
    ) -> tuple[List[Dict], List[str], str, List[str], int]:
        # Step 1: 建立 Qdrant filter
        must_conditions = []

        if categories:
            for cat in categories:
                if cat:
                    must_conditions.append(
                        models.FieldCondition(
                            key="categories", match=models.MatchValue(value=cat)
                        )
                    )

        filter_cond = models.Filter(must=must_conditions) if must_conditions else None

        logger.info(f"filter_cond {filter_cond}")
        # Step 2: Qdrant search
        # Hybrid search：向量 + filter

        if hybrid:
            # 🚀 Hybrid search (dense + sparse)
            logger.info("Hybrid search (dense + sparse)")

            query_result = self.client.query_points(
                collection_name=self.settings.COLLECTION_NAME,
                prefetch=[
                    models.Prefetch(query=query_vector, using="dense", limit=5 * size),
                    models.Prefetch(
                        query=models.Document(
                            text=query,
                            model="Qdrant/bm25",
                        ),
                        using="bm25",
                        limit=5 * size,
                    ),
                ],
                # Fusion query enables fusion on the prefetched results
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=size,
                with_payload=True,
            )

        else:
            logger.info("Dense-only search")
            # 🚀 Dense-only search
            query_result = self.client.query_points(
                collection_name=self.settings.COLLECTION_NAME,
                query=query_vector,
                using="dense",
                limit=size,
                with_payload=True,
            )
            # query_result = self.client.query_points(
            #     collection_name=self.settings.COLLECTION_NAME,
            #     query=models.Document(
            #         text=query,
            #         model="Qdrant/bm25",
            #     ),
            #     using="bm25",
            #     limit=size,
            #     with_payload=True,
            # )

        # Extract essential data for LLM
        chunks = []
        arxiv_ids = []
        sources = set()

        # [ScoredPoint(id=2952, version=30, score=0.591295, payload= {'arxiv_id' : XXX, 'abstract': XXX, 'title': XXX, 'authors': XXX, 'categories': XXX, 'published_date': XXX, 'text': XXX, 'chunk_idx': XXX}
        msg = ""
        for hit in query_result.points:
            if hit.score < min_score:
                continue
            payload = hit.payload
            # logger.info(f"payload {payload}")
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

        logger.info(
            f"search found {len(chunks)} chunks, {len(sources)} sources\n\n with filter {filter_cond}\n\n"
        )

        return chunks, list(sources), msg, arxiv_ids, len(query_result.points)
