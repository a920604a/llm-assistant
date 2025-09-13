from arxiv_ingestion.services.embedding import get_embedding
from config import settings
from logger import AppLogger
from qdrant_client import models
from storage.qdrant import qdrant_client

logger = AppLogger(__name__).get_logger()


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

    logger.info(f"filter_cond {filter_cond}")
    # Step 2: Qdrant search
    query_result = qdrant_client.search(
        collection_name=settings.COLLECTION_NAME,
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
    msg = f"Retrieved {len(results)} chunks from collection '{settings.COLLECTION_NAME}':\n{chunks_info_str}"

    return (
        results,
        msg,
    )


if __name__ == "__main__":
    # 測試 query
    query_title = (
        "Mini-o3: Scaling Up Reasoning Patterns and Interaction Turns for Visual Search"
    )

    # 可選 filter
    category_filter = "cs.CV"
    author_filter = None
    start_date_filter = None
    end_date_filter = None
    top_k = 5

    # 呼叫 retrieval
    results, msg = retrieval(
        query=query_title,
        top_k=top_k,
        category=category_filter,
        author=author_filter,
        start_date=start_date_filter,
        end_date=end_date_filter,
    )

    print("\n=== Retrieval Result ===")
    print(msg)
    for idx, chunk in enumerate(results):
        print(f"\n--- Chunk {idx} ---")
        print(f"arxiv_id: {chunk['arxiv_id']}")
        print(f"title: {chunk['title']}")
        print(f"chunk_idx: {chunk['chunk_idx']}")
        print(f"text snippet: {chunk['text'][:200]}...")  # 只顯示前 200 字
