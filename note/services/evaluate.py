import math
from typing import List

from dependencies import QdrantDep
from services.embedding import get_embedding


# ---------------- 評估函數 ----------------
def ndcg_at_k(ranked_ids: List[str], ground_truth_ids: List[str], k: int = 5):
    dcg = 0.0
    for i, id_ in enumerate(ranked_ids[:k]):
        if id_ in ground_truth_ids:
            dcg += 1.0 / math.log2(i + 2)
    ideal_dcg = sum(
        1.0 / math.log2(i + 2) for i in range(min(k, len(ground_truth_ids)))
    )
    return dcg / ideal_dcg if ideal_dcg > 0 else 0.0


def mrr_at_k(ranked_ids: List[str], ground_truth_ids: List[str], k: int = 5):
    for i, id_ in enumerate(ranked_ids[:k]):
        if id_ in ground_truth_ids:
            return 1.0 / (i + 1)
    return 0.0


def hit_rate(ranked_ids: List[str], ground_truth_ids: List[str], k: int = 5):
    top_ids = ranked_ids[:k]
    hits = sum(1 for id_ in top_ids if id_ in ground_truth_ids)
    return hits / min(k, len(ground_truth_ids))


def generate_pseudo_ground_truth(
    qdrant_client: QdrantDep, query: str, top_n: int = 5, hybrid_search: bool = False
):
    """
    使用 query embedding 從 Qdrant search 出 top_n 當作 pseudo ground truth
    """
    query_emb = get_embedding(query)

    results = qdrant_client.search_native(
        query_vector=query_emb, query=query, size=top_n, hybrid_search=hybrid_search
    )

    # 返回 arxiv_id list 作為 ground truth
    pseudo_gt = [hit.payload["arxiv_id"] for hit in results]
    return pseudo_gt


def evaluate(
    qdrant_client: QdrantDep,
    reranked_chunks: list,
    query: str,
    top_k: int = 5,
    hybrid_search: bool = False,
) -> dict:
    """
    Evaluate retrieval + rerank 表現
    """

    pseudo_gt = generate_pseudo_ground_truth(
        qdrant_client, query, top_n=top_k, hybrid_search=hybrid_search
    )
    ranked_ids = [chunk["arxiv_id"] for chunk in reranked_chunks]

    ndcg = ndcg_at_k(ranked_ids, pseudo_gt, k=top_k)
    mrr = mrr_at_k(ranked_ids, pseudo_gt, k=top_k)
    hit = hit_rate(ranked_ids, pseudo_gt, k=top_k)

    return {"ndcg": ndcg, "mrr": mrr, "hit_rate": hit, "ranked_ids": ranked_ids}
