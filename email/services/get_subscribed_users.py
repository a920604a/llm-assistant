from typing import Dict, List

from fastapi import HTTPException
from prefect import get_run_logger
from services.get_user_email_from_firebase import get_user_email_from_firebase
from sqlalchemy.orm import Session
from storage.model import User, UserSetting  # 假設 ORM model


def get_subscribed_users(db: Session) -> List[Dict]:
    logger = get_run_logger()
    """
    返回訂閱郵件的用戶資訊
    每個 user dict 包含:
    - user_id
    - email
    - translate
    - user_language
    """
    subscribed_users = []
    try:
        # join users 與 user_setting
        query = (
            db.query(User, UserSetting)
            .join(UserSetting, User.id == UserSetting.user_id)
            .filter(UserSetting.subscribe_email)
        )
        for user, setting in query.all():
            try:
                email = get_user_email_from_firebase(user.id)
            except HTTPException:
                logger.warning(f"Skipping user {user.id}, no email found")
                continue

            subscribed_users.append(
                {
                    "user_id": user.id,
                    "email": email,
                    "translate": setting.translate,
                    "user_language": setting.user_language,
                }
            )

    except Exception as e:
        logger.error(f"Error fetching subscribed users: {e}")
        raise e

    logger.info(f"Total subscribed users fetched: {len(subscribed_users)}")
    return subscribed_users
