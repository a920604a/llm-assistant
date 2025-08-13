from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
import os
from api.verify_token import verify_token

security = HTTPBearer()

router = APIRouter()

UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/api/upload")
async def upload_files(files: list[UploadFile] = File(...), user=Depends(verify_token)):
    user_id = user.get("uid")
    saved_files = []

    for file in files:
        file_location = os.path.join(UPLOAD_DIR, f"{user_id}_{file.filename}")
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_files.append(file.filename)

    return {
        "message": f"成功上傳 {len(saved_files)} 個檔案",
        "files": saved_files,
        "user_id": user_id,
    }
