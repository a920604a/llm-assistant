# tasks/upload.py
import traceback
from celery_app import celery_app
from note_workflow.ingest_pipeline import ingest_notes_pipeline
from storage.minio import s3_client, MINIO_BUCKET

from logger import get_logger

logger = get_logger(__name__)




# tasks/upload.py
@celery_app.task(name="import_single_md_task")
def import_single_md_task(user_id: str, filename: str):
    try:
        # 從 MinIO 讀檔
        obj = s3_client.get_object(Bucket=MINIO_BUCKET, Key=filename)
        content = obj["Body"].read().decode("utf-8")

        # 傳給流程處理
        ingest_notes_pipeline({filename: content})
        return f"{filename} 處理完成"

    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}
