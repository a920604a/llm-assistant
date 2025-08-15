from fastapi import APIRouter
from services.note import get_notes


router = APIRouter()


@router.get("/api/user_notes/{user_id}")
def get_user_notes(user_id: str):
    return get_notes(user_id)
