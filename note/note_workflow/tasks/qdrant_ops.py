from conf import COLLECTION_NAME
from logger import get_logger
from prefect import task
from storage.qdrant import qdrant_client

logger = get_logger(__name__)


@task
def upload_points(points: list):
    if not points:
        logger.warning("⚠️ No points to upload")
        return
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    logger.info(f"✅ Uploaded {len(points)} points to Qdrant ({COLLECTION_NAME})")
