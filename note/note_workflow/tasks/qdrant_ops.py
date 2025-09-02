from config import COLLECTION_NAME
from logger import AppLogger
from prefect import task
from storage.qdrant import qdrant_client

logger = AppLogger(__name__).get_logger()


@task
def upload_points(points: list):
    if not points:
        logger.warning("⚠️ No points to upload")
        return
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    logger.info(f"✅ Uploaded {len(points)} points to Qdrant ({COLLECTION_NAME})")
