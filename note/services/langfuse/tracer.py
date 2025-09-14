"""Simple, efficient Langfuse tracing utility for RAG pipeline."""

from contextlib import contextmanager
from typing import Dict, List

from services.langfuse.client import LangfuseTracer


class RAGTracer:
    """Clean, purpose-built tracer for RAG operations."""

    def __init__(self, tracer: LangfuseTracer):
        self.tracer = tracer

    @contextmanager
    def trace_request(self, user_id: str, query: str):
        """Main request trace context manager."""
        with self.tracer.trace_rag_request(
            query=query,
            user_id=user_id,
            session_id=f"session_{user_id}",
            metadata={"simplified_tracing": True},
        ) as trace:
            try:
                yield trace
            finally:
                if trace:
                    self.tracer.flush()

    @contextmanager
    def trace_embedding(self, trace, query: str):
        """Query embedding operation with timing."""
        span = self.tracer.create_span(
            trace=trace,
            name="query_embedding",
            input_data={"query": query, "query_length": len(query)},
        )
        try:
            yield span
        finally:
            if span:
                self.tracer.update_span(
                    span=span,
                    output={
                        "success": True,
                    },
                )
                span.end()

    def end_embedding(self, span, embedding_vector: list[float]):
        """
        End embedding span with the resulting vector and duration.

        Args:
            span: The span object created by trace_embedding
            embedding_vector: The resulting embedding vector
        """
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "embedding_length": len(embedding_vector),
                "embedding_vector_preview": embedding_vector[
                    :10
                ],  # 只取前10個元素避免過長
            },
        )
        span.end()

    @contextmanager
    def trace_search(self, trace, query: str, top_k: int):
        """Search operation with timing."""
        span = self.tracer.create_span(
            trace=trace,
            name="search_retrieval",
            input_data={"query": query, "top_k": top_k},
        )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_search(
        self, span, chunks: List[Dict], arxiv_ids: List[str], total_hits: int
    ):
        """End search span with essential results."""
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "chunks_returned": len(chunks),
                "unique_papers": len(set(arxiv_ids)),
                "total_hits": total_hits,
                "arxiv_ids": list(set(arxiv_ids)),
            },
        )

    @contextmanager
    def trace_rerank(
        self, trace, query: str, vector_weight: float = 0.6, bm25_weight: float = 0.3
    ):
        """
        Rerank operation with timing (vector + BM25 hybrid).
        """
        span = self.tracer.create_span(
            trace=trace,
            name="rerank",
            input_data={
                "query": query,
                "vector_weight": vector_weight,
                "bm25_weight": bm25_weight,
            },
        )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_rerank(self, span, reranked_chunks: list[dict]):
        """
        End rerank span and report top results.
        """
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "reranked_chunk_count": len(reranked_chunks),
                "top_chunk_ids": [c.get("arxiv_id") for c in reranked_chunks[:10]],
                "top_scores": [c.get("total_score") for c in reranked_chunks[:10]],
            },
        )

    @contextmanager
    def trace_evaluate(self, trace, query: str, reranked_chunks: list, top_k: int = 5):
        """
        Evaluation of reranked results with timing.
        """
        span = self.tracer.create_span(
            trace=trace,
            name="rerank_evaluation",
            input_data={
                "query": query,
                "top_k": top_k,
                "reranked_chunks": reranked_chunks,
            },
        )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_evaluate(self, span, eval_metrics: dict):
        """
        End evaluation span and report metrics.
        """
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "ndcg": eval_metrics.get("ndcg"),
                "mrr": eval_metrics.get("mrr"),
                "hit_rate": eval_metrics.get("hit_rate"),
                "ranked_ids": eval_metrics.get("ranked_ids", [])[
                    :10
                ],  # top 10 for logging
            },
        )

    @contextmanager
    def trace_prompt_construction(self, trace, chunks: List[Dict]):
        """Prompt building with timing."""
        span = self.tracer.create_span(
            trace=trace,
            name="prompt_construction",
            input_data={"chunk_count": len(chunks)},
        )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_prompt(self, span, prompt: str):
        """End prompt span with final prompt."""
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "prompt_length": len(prompt),
                # Don't duplicate the full prompt here since it's in llm_generation input
                "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            },
        )

    @contextmanager
    def trace_generation(self, trace, model: str, prompt: str):
        """LLM generation with timing."""
        span = self.tracer.create_span(
            trace=trace,
            name="llm_generation",
            input_data={"model": model, "prompt_length": len(prompt), "prompt": prompt},
        )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_generation(self, span, response: str, model: str):
        """End generation span with response."""
        if not span:
            return

        self.tracer.update_span(
            span=span,
            output={
                "response": response,
                "response_length": len(response),
                "model_used": model,
            },
        )

    def end_request(self, trace, response: str, total_duration: float):
        """End main request trace."""
        if not trace:
            return

        try:
            trace.update(
                output={
                    "answer": response,
                    "total_duration_seconds": round(total_duration, 3),
                    "response_length": len(response),
                }
            )
        except Exception:
            # Silently fail - don't break the request for tracing issues
            pass
