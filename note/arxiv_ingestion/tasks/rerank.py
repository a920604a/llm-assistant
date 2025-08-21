import jieba
from prefect import task
from rank_bm25 import BM25Okapi


@task(name="Hybrid Reranking Task")
def re_ranking(
    chunks: list,
    query: str,
    vector_weight: float = 0.6,
    bm25_weight: float = 0.3,
    field_weights: dict = None,
):
    """
    Hybrid reranking: vector similarity + BM25 text matching + 欄位加權
    chunks: list of payload dict，需包含 text/title/abstract 與向量相似度 score
    field_weights: 欄位權重，例如 {'text':1.0, 'title':0.8, 'abstract':0.5}
    """
    if field_weights is None:
        field_weights = {"text": 1.0, "title": 0.8, "abstract": 0.5}

    query_tokens = list(jieba.cut(query.lower()))

    scored_chunks = []

    for chunk in chunks:
        # 1️⃣ Vector similarity
        vector_score = chunk.get("score", 1.0)  # 假設 retrieval 已給向量相似度

        # 2️⃣ BM25 score
        bm25_total = 0.0
        for field, weight in field_weights.items():
            content = chunk.get(field, "")
            if not content:
                continue
            tokens = list(jieba.cut(content.lower()))
            bm25 = BM25Okapi([tokens])
            score = bm25.get_scores(query_tokens)[0]  # 單篇文件的 BM25 分數
            bm25_total += weight * score

        # 3️⃣ Combine scores
        total_score = vector_weight * vector_score + bm25_weight * bm25_total
        scored_chunks.append((total_score, chunk))

    # 排序
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    reranked_chunks = [chunk for score, chunk in scored_chunks]
    return reranked_chunks
