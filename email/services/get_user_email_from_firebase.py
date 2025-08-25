from fastapi import HTTPException
from firebase_admin import auth as firebase_auth
from prefect import get_run_logger


def get_user_email_from_firebase(user_id: str) -> str:
    logger = get_run_logger()

    try:
        user_record = firebase_auth.get_user(user_id)
        return user_record.email
    except Exception as e:
        logger.error(f"Failed to get Firebase user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Cannot get email for user {user_id}"
        )
