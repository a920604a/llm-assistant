# REST API routers
from fastapi import APIRouter, HTTPException
from services.user_info import get_user_info

router = APIRouter()


@router.get("/api/user/{user_id}")
def get_user_data(user_id: str):
    # user_id 是 str，如果要檢查是否為有效 id，視情況可轉 int 或用正則判斷
    if not user_id or len(user_id) == 0:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    info = get_user_info(user_id)
    if not info:
        raise HTTPException(status_code=404, detail="User not found")

    return info
