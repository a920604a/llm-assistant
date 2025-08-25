from arxiv_ingestion.config import COLLECTION_NAME
from arxiv_ingestion.db.qdrant import qdrant_client
from arxiv_ingestion.services.embedding import get_embedding
from prefect import task
from qdrant_client import models


@task
# def retrieval(query: str, top_k: int = 5, course: str = "data-engineering-zoomcamp"):
def retrieval(
    query: str,
    top_k: int = 5,
    category: str = None,
    author: str = None,
    title: str = None,
    start_date: str = None,  # e.g. "2023-01-01"
    end_date: str = None,
) -> tuple[list, str]:
    # Step 1: embedding query
    query_vector = get_embedding(query)

    # Step 2: 建立 Qdrant filter
    must_conditions = []
    if category:
        must_conditions.append(
            models.FieldCondition(
                key="categories", match=models.MatchValue(value=category)
            )
        )
    if author:
        must_conditions.append(
            models.FieldCondition(key="authors", match=models.MatchValue(value=author))
        )
    if title:
        must_conditions.append(
            models.FieldCondition(
                key="title",
                match=models.MatchValue(value=title),
            )
        )
    if start_date or end_date:
        # published_date 篩選
        date_range = {}
        if start_date:
            date_range["gte"] = start_date
        if end_date:
            date_range["lte"] = end_date
        must_conditions.append(
            models.Range(key="published_date", gte=start_date, lte=end_date)
        )
    filter_cond = models.Filter(must=must_conditions) if must_conditions else None

    # Step 2: Qdrant search
    query_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=filter_cond,
        limit=top_k,
        with_payload=True,
    )

    results = [hit.payload for hit in query_result]
    # [ {'arxiv_id' : XXX, 'abstract': XXX, 'title': XXX, 'authors': XXX, 'categories': XXX, 'published_date': XXX, 'text': XXX, 'chunk_idx': XXX}, ]
    chunks_info_str = "\n".join(
        [f"{chunk['title']} ({chunk['arxiv_id']})" for chunk in results]
    )
    msg = f"Retrieved {len(results)} chunks from collection '{COLLECTION_NAME}':\n{chunks_info_str}"

    return (
        results,
        msg,
    )
