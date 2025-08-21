from typing import Dict, List

from prefect import task


@task
def build_prompt(query: str, retrieved_chunks: List[Dict]) -> str:
    context = (
        "\n".join([c["text"] for c in retrieved_chunks[:3]]) if retrieved_chunks else ""
    )
    prompt = f"User question: {query}\nRelevant context:\n{context}\nPlease answer the question based on the above context."
    return prompt
