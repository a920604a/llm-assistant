import io
from typing import List

from config import COLLECTION_NAME, MINIO_BUCKET
from db.minio import s3_client
from db.qdrant import qdrant_client
from logger import get_logger
from prefect import task
from qdrant_client import models
from services.embedding import get_embedding
from services.pdf_parser import TextExtractor
from services.schemas import ArxivPaper

logger = get_logger(__name__)


# 可以依需要調整 chunk_size 與 overlap
CHUNK_SIZE = 500  # token 或字數，根據你的 embedding 模型調整
CHUNK_OVERLAP = 50


def chunk_text(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    將長文本切分成多個 chunk
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # 保留 overlap
        if start < 0:
            start = 0
        if start >= text_length:
            break
    return chunks


@task(name="Qdrant Index Task")
def qdrant_index_task(papers: List[ArxivPaper]):
    """
    將 papers 轉成向量並上傳到 Qdrant
    """
    points: List[models.PointStruct] = []
    idx = 0

    textExtractor = TextExtractor()

    for paper in papers:
        buffer = io.BytesIO()
        # 從 MinIO 下載 PDF 到記憶體
        s3_client.download_fileobj(
            MINIO_BUCKET, f"{paper.arxiv_id}/{paper.arxiv_id}.pdf", buffer
        )
        buffer.seek(0)
        sections, all_text = textExtractor.extract(buffer)

        text = "\n".join(all_text)
        print(f"{paper.arxiv_id} 抽取文字長度: {len(text)}")

        if not text:
            continue

        metadata = {
            "arxiv_id": paper.arxiv_id,
            "abstract": paper.abstract,
            "title": paper.title,
            "authors": paper.authors,
            "categories": paper.categories,
            "published_date": paper.published_date,
        }

        # 切分 chunk
        chunks = chunk_text(text)
        for chunk_idx, chunk in enumerate(chunks):
            vector = get_embedding(chunk)

            payload = {**metadata, "text": chunk, "chunk_idx": chunk_idx}

            points.append(models.PointStruct(id=idx, vector=vector, payload=payload))
            idx += 1

    if points:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info(f"✅ 已上傳 {len(points)} 個 papers 到 Qdrant")
    else:
        logger.warning("⚠️ 無可上傳的 papers 到 Qdrant")

    return len(points)
