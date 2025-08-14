from datetime import date
import os
import logging

from storage.minio import s3_client, create_bucket_if_not_exists, MINIO_BUCKET
from storage.crud.user import get_user_notes_number
from storage.crud.note import update_note
from tasks.upload import import_md_notes_task


logger = logging.getLogger(__name__)


UPLOAD_DIR = "./uploaded_files"


async def upload_notes(files, user_id: str):
    logger.info("upload_notes")
    uploaded_notes = get_user_notes_number(user_id)

    # save minIO or local file
    md_text_dict, saved_files = await upload_files(files, user_id)
    md_text_dict, saved_files = await upload_files(
        files, user_id, True
    )  # save local storage

    # save postgres
    update_note(
        user_id,
        uploaded_notes=uploaded_notes + len(saved_files),
        last_query_date=date.today(),
    )
    logger.info("update_user")

    # 透過 Celery 背景執行 flow
    if md_text_dict:
        logger.info("透過 Celery 背景執行 flow")
        import_md_notes_task.apply_async(args=[md_text_dict], queue="notes")

    return {
        "message": f"成功上傳 {len(saved_files)} 個檔案",
        "files": saved_files,
        "user_id": user_id,
    }


async def upload_files(files, user_id: str, save_local=False):
    saved_files = []
    md_text_dict = {}
    if save_local:
        # 確保目錄存在
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        for file in files:
            file_location = os.path.join(UPLOAD_DIR, f"{user_id}_{file.filename}")
            with open(file_location, "wb") as f:
                content = await file.read()
                f.write(content)
            saved_files.append(file.filename)
            if file.filename.endswith(".md"):
                md_text_dict[file.filename] = content.decode("utf-8")
    else:
        create_bucket_if_not_exists()

        for file in files:
            if not file.filename.endswith(".md"):
                continue

            content = await file.read()
            md_text_dict[file.filename] = content.decode("utf-8")

            # 上傳到 MinIO
            s3_client.put_object(
                Bucket=MINIO_BUCKET,
                Key=file.filename,
                Body=content,
                ContentType="text/markdown",
            )

            saved_files.append(file.filename)

    return md_text_dict, saved_files
