# tasks/upload.py
import logging
from celery_app import celery_app
from services.workflow.ingest import import_md_notes_flow
import traceback


logger = logging.getLogger(__name__)


@celery_app.task(name="import_md_notes_task")
def import_md_notes_task(md_text_dict: dict):
    # md_text_dict  = {"file_path" : text}
    logger.info(f"md_text_dict {md_text_dict}")
    try:
        import_md_notes_flow(md_text_dict)
        return f"處理 {len(md_text_dict)} 個 Markdown 檔案完成"
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}
