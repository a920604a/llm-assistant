import json
import math
from typing import List

from logger import AppLogger
from services.embedding import get_embedding
from services.ollama.client import OllamaClient
from services.qdrant.client import QdrantClient

logger = AppLogger(__name__).get_logger()


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
    qdrant_client: QdrantClient, query: str, top_n: int = 5, hybrid_search: bool = False
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


async def evaluate(
    ollama_client: OllamaClient,
    question: str,
    answer: str,
) -> dict:
    """
    Evaluate retrieval + rerank 表現
    """
    evaluation_prompt_template = """
        You are an expert evaluator for a RAG system.
        Classify the answer relevance as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

        Question: {question}
        Generated Answer: {answer_llm}

        Return ONLY JSON like:
        {{"Relevance": "NON_RELEVANT", "Explanation": "Brief explanation"}}
        """

    logger.info(f"EVALUATE question {question}")
    logger.info(f"EVALUATE answer {answer}")

    prompt = evaluation_prompt_template.format(question=question, answer_llm=answer)
    logger.info(f"EVALUATE prompt {prompt}")

    resp = await ollama_client.generate(prompt=prompt)
    logger.info(f"EVALUATE {resp}")
    evaluation = resp.get("response", "")

    try:
        eval_metrics = json.loads(evaluation)
        logger.info(f"eval_metrics {eval_metrics}")
        return eval_metrics

    except json.JSONDecodeError:
        return {
            "Relevance": "UNKNOWN",
            "Explanation": "Failed to parse evaluation",
        }
