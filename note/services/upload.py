from datetime import date
import os

from storage.minio import s3_client, create_bucket_if_not_exists, MINIO_BUCKET
from storage.crud.user import get_user_notes_number
from storage.crud.note import update_notes
from tasks.upload import import_md_notes_task, import_single_md_task

from logger import get_logger

logger = get_logger(__name__)

UPLOAD_DIR = "./uploaded_files"


async def upload_notes(files, user_id: str):
    logger.info("upload_notes")
    uploaded_notes = get_user_notes_number(user_id)

    # 儲存檔案（本地或 MinIO）
    result = await upload_files(files, user_id, save_local=False, save_minio=True)

    logger.info(f"成功檔案: {result['saved_files']}")
    logger.info(f"失敗檔案: {result['failed_files']}")
    logger.info(f"總檔案大小: {result['total_size']} bytes")

    # save user table postgres
    update_notes(user_id, result["saved_files"])
    logger.info("update_notes")

    # 透過 Celery 背景執行 flow
    for filename in result["saved_files"]:
        import_single_md_task.apply_async(args=[user_id, filename], queue="notes")

    return {
        "message": (
            f"成功上傳 {len(result['saved_files'])} 個檔案"
            + (
                f"，失敗 {len(result['failed_files'])} 個"
                if result["failed_files"]
                else ""
            )
        ),
        "files": result["saved_files"],
        "user_id": user_id,
    }


async def upload_files(files, user_id: str, save_local=False, save_minio=True):
    saved_files = []
    failed_files = []
    md_text_dict = {}

    if save_local:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    if save_minio:
        create_bucket_if_not_exists()

    for file in files:
        if not file.filename.endswith(".md"):
            logger.info(f"略過非 markdown 檔案: {file.filename}")
            continue

        try:
            # ⚠ 一次讀取避免多次讀導致空檔案
            content = await file.read()
            if not content:
                logger.warning(f"{file.filename} 無內容或讀取失敗")
                failed_files.append(file.filename)
                continue

            md_text_dict[file.filename] = content.decode("utf-8")
            saved_files.append(file.filename)

            if save_local:
                try:
                    file_location = os.path.join(
                        UPLOAD_DIR, f"{user_id}_{file.filename}"
                    )
                    with open(file_location, "wb") as f:
                        f.write(content)
                    logger.info(f"已儲存本地: {file_location}")
                except Exception as e:
                    logger.error(f"儲存本地失敗 {file.filename}: {e}")
                    failed_files.append(file.filename)
                    continue

            if save_minio:
                try:
                    s3_client.put_object(
                        Bucket=MINIO_BUCKET,
                        Key=file.filename,
                        Body=content,
                        ContentType="text/markdown",
                    )
                    logger.info(f"已上傳 MinIO: {file.filename} ({len(content)} bytes)")
                except Exception as e:
                    logger.error(f"上傳 MinIO 失敗 {file.filename}: {e}")
                    failed_files.append(file.filename)
                    continue

        except Exception as e:
            logger.error(f"處理檔案 {file.filename} 時發生錯誤: {e}")
            failed_files.append(file.filename)

    return {
        "md_text_dict": md_text_dict,
        "saved_files": saved_files,
        "failed_files": failed_files,
        "total_size": sum(len(c.encode("utf-8")) for c in md_text_dict.values()),
    }
