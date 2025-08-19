from prefect import task
from typing import List

@task
def re_ranking(chunks: List[dict], query: str) -> List[dict]:
    query_tokens = query.lower().split()
    sorted_chunks = sorted(
        chunks,
        key=lambda c: sum(1 for token in query_tokens if token in c.get("text", "").lower()),
        reverse=True
    )
    return sorted_chunks
