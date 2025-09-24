"""Simple, efficient Langfuse tracing utility for RAG pipeline."""

from contextlib import contextmanager

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

    @contextmanager
    def trace_prompt_construction(self, trace, prompt: str):
        """Prompt building with timing."""
        span = self.tracer.create_span(
            trace=trace,
            name="prompt_construction",
            input_data={"prompt_count": len(prompt)},
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
