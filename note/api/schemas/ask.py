from typing import List, Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request model for RAG question answering."""

    user_id: str = Field(..., description="User's id", min_length=1, max_length=1000)
    query: str = Field(
        ..., description="User's question", min_length=1, max_length=1000
    )
    top_k: int = Field(3, description="Number of top chunks to retrieve", ge=1, le=50)
    use_hybrid: bool = Field(True, description="Use hybrid search (BM25 + vector)")
    model: str = Field("llama3.2:1b", description="Ollama model to use for generation")
    categories: Optional[List[str]] = Field(
        None, description="Filter by arXiv categories"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "RFGBDRFBGFNA",
                "query": "What are transformers in machine learning?",
                "top_k": 3,
                "use_hybrid": True,
                "model": "llama3.2:1b",
                "categories": ["cs.AI", "cs.LG"],
            }
        }


class AskResponse(BaseModel):
    """Response model for RAG question answering."""

    query: str = Field(..., description="Original user question")
    answer: str = Field(..., description="Generated answer from LLM")
    sources: List[str] = Field(..., description="PDF URLs of source papers")
    chunks_used: int = Field(..., description="Number of chunks used for generation")
    search_mode: str = Field(..., description="Search mode used: bm25 or hybrid")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are transformers in machine learning?",
                "answer": "Transformers are a neural network architecture...",
                "sources": [
                    "https://arxiv.org/pdf/1706.03762.pdf",
                    "https://arxiv.org/pdf/1810.04805.pdf",
                ],
                "chunks_used": 3,
                "search_mode": "hybrid",
            }
        }


class GradioStreamRequest(BaseModel):
    """Request model for Gradio streaming."""

    query: str = Field(
        ..., description="User's question", min_length=1, max_length=1000
    )
    top_k: int = Field(3, description="Number of top chunks to retrieve", ge=1, le=10)
    use_hybrid: bool = Field(True, description="Use hybrid search ")
    model: str = Field("gpt-oss:20b", description="Ollama model to use for generation")
    categories: Optional[List[str]] = Field(
        None, description="Filter by arXiv categories"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are transformers in machine learning?",
                "top_k": 3,
                "use_hybrid": True,
                "model": "gpt-oss:20b",
                "categories": ["cs.AI", "cs.LG"],
            }
        }
