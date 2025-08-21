from conf import COLLECTION_NAME
from logger import get_logger
from prefect import task
from qdrant_client import models
from services.embedding import get_embedding
from storage.qdrant import qdrant_client

logger = get_logger(__name__)


@task
def retrieval(query: str, top_k: int = 5, course: str = "data-engineering-zoomcamp"):
    # Step 1: embedding query
    query_vector = get_embedding(query)

    # Step 2: Qdrant search
    query_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="course", match=models.MatchValue(value=course)
                )
            ]
        ),
        limit=top_k,
        with_payload=True,
    )

    results = [hit.payload for hit in query_result]
    logger.info(f"Retrieved {len(results)} chunks from collection '{COLLECTION_NAME}'")
    return results
