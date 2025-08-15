import requests
from conf import NOTE_API_URL
from fastapi import FastAPI, UploadFile
import requests
from conf import NOTE_API_URL
import anyio


async def upload_notes(user_id: str, files: list[UploadFile]):
    # 準備 form-data
    multipart_files = []
    for file in files:
        content = await file.read()  # 讀取檔案內容
        multipart_files.append(("files", (file.filename, content, file.content_type)))

    # 同步請求，但包在 async context 裡
    def send_request():
        return requests.post(
            f"{NOTE_API_URL}/api/upload",
            files=multipart_files,
            data={"user_id": user_id}  # user_id 放 form 欄位
        )

    resp = await anyio.to_thread.run_sync(send_request)
    resp.raise_for_status()

    return resp.json()
