from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
import os
from services.upload import upload_notes

from api.verify_token import verify_token


router = APIRouter()

UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

import logging

logger = logging.getLogger(__name__)


@router.post("/api/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    user=Depends(verify_token),  # 驗證 token，取得 user info
):

    user_id = user.get("uid")
    await upload_notes(user_id, files)

    return {
        "message": f"成功上傳 ",
        "user_id": user_id,
    }
