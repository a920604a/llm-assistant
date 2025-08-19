import os

from fastapi import APIRouter, UploadFile, File, Form
from services.upload import upload_notes

UPLOAD_DIR = "/data/uploaded_files"
router = APIRouter()


@router.post("/api/upload")
async def upload_files(files: list[UploadFile] = File(...), user_id: str = Form(...)):
    ret = await upload_notes(files, user_id)

    return {
        "message": ret["message"],
        "files": ret["files"],
        "user_id": ret["user_id"],
    }
