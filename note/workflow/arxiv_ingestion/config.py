from pydantic import BaseSettings, Field


PDF_CACHE_DIR = "./data/arxiv_pdfs"

class DefaultSettings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"
        frozen = True

class ArxivSettings(DefaultSettings):
    api_base_url: str = "https://export.arxiv.org/api/query"
    cache_dir: str = "/app/cache/arxiv_pdfs"  # 或你想存 PDF 的路徑
    # base_url: str = "https://export.arxiv.org/api/query"
    pdf_cache_dir: str = PDF_CACHE_DIR
    namespaces: dict = Field(
        default={
            "atom": "http://www.w3.org/2005/Atom",
            "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
    )
    rate_limit_delay: float = 3.0  # seconds between requests
    timeout_seconds: int = 30
    max_results: int = 100
    search_category: str = "cs.AI"  # 預設抓 cs.AI 分類
