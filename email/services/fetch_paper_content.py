from config import COLLECTION_NAME
from prefect import get_run_logger
from qdrant_client import models
from storage.qdrant_client import qdrant_client


def fetch_paper_content_from_qdrant(arxiv_id: str = None, title: str = None) -> str:
    """
    從 Qdrant 依 arxiv_id 或 title 抓取 raw_content
    """
    logger = get_run_logger()

    must_conditions = []
    if arxiv_id:
        must_conditions.append(
            models.FieldCondition(
                key="arxiv_id",
                match=models.MatchValue(value=arxiv_id),
            )
        )
    if title:
        must_conditions.append(
            models.FieldCondition(
                key="title",
                match=models.MatchValue(value=title),
            )
        )

    if not must_conditions:
        logger.warning("No arxiv_id or title provided for Qdrant fetch")
        return ""

    logger.info(f"Qdrant query must_conditions: {must_conditions}")
    result = qdrant_client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=models.Filter(must=must_conditions),
        limit=1,
    )

    points, _ = result
    logger.info(f"Qdrant returned {len(points)} points for arxiv_id={arxiv_id}")
    if not points:
        return ""

    payload = points[0].payload
    raw_content = payload.get("text", "")
    logger.debug(f"Fetched raw_content length: {len(raw_content)}")
    return raw_content
