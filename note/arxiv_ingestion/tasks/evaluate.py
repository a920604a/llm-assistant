from arxiv_ingestion.config import COLLECTION_NAME
from arxiv_ingestion.db.qdrant import qdrant_client
from arxiv_ingestion.services.embedding import get_embedding
from arxiv_ingestion.services.metrics import hit_rate, mrr_at_k, ndcg_at_k
from prefect import task


def generate_pseudo_ground_truth(query: str, top_n: int = 5):
    """
    使用 query embedding 從 Qdrant search 出 top_n 當作 pseudo ground truth
    """
    query_emb = get_embedding(query)

    results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_emb,
        limit=top_n * 2,
        with_payload=True,
    )

    # 返回 arxiv_id list 作為 ground truth
    pseudo_gt = [hit.payload["arxiv_id"] for hit in results]
    return pseudo_gt


@task
def evaluate(reranked_chunks: list, query: str, top_k: int = 5) -> dict:
    """
    Evaluate retrieval + rerank 表現
    """

    pseudo_gt = generate_pseudo_ground_truth(query, top_n=top_k)
    ranked_ids = [chunk["arxiv_id"] for chunk in reranked_chunks]

    ndcg = ndcg_at_k(ranked_ids, pseudo_gt, k=top_k)
    mrr = mrr_at_k(ranked_ids, pseudo_gt, k=top_k)
    hit = hit_rate(ranked_ids, pseudo_gt, k=top_k)

    return {"ndcg": ndcg, "mrr": mrr, "hit_rate": hit, "ranked_ids": ranked_ids}
