from services.user import get_user, update_user
from tasks.upload import import_md_notes_task
from datetime import date
import os
import logging


logger = logging.getLogger(__name__)



UPLOAD_DIR = "./uploaded_files"



async def upload_notes(files, user_id: str):
    logger.info("upload_notes")
    user = get_user(user_id)
    # 確保目錄存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    saved_files = []
    md_text_dict = {}

    for file in files:
        file_location = os.path.join(UPLOAD_DIR, f"{user_id}_{file.filename}")
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_files.append(file.filename)
        if file.filename.endswith(".md"):
            md_text_dict[file.filename] = content.decode("utf-8")

    # update_user(user_id, ...)
    new_uploaded_notes = user["uploaded_notes"] + len(saved_files)
    update_user(
        user_id,
        uploaded_notes=new_uploaded_notes,
        last_query_date=date.today()
    )
    logger.info("update_user")
    
    # 透過 Celery 背景執行 flow
    if md_text_dict:
        logger.info("透過 Celery 背景執行 flow")
        task_result = import_md_notes_task.apply_async(args=[md_text_dict], queue="notes")
    
    
    

    return {
        "message": f"成功上傳 {len(saved_files)} 個檔案",
        "files": saved_files,
        "user_id": user_id,
    }


