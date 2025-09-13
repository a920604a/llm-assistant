import math
from typing import List


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
