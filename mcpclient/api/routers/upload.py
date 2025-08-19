from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
import os
from services.upload import upload_notes

from api.verify_token import verify_token


router = APIRouter()


from logger import get_logger

logger = get_logger(__name__)


@router.post("/api/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    user=Depends(verify_token),  # 驗證 token，取得 user info
):

    user_id = user.get("uid")
    ret = await upload_notes(user_id, files)
    logger.info(f"note {ret} user_id {user_id}")

    return {
        "message": ret["message"],
        "files": ret["files"],
        "user_id": user_id,
    }
