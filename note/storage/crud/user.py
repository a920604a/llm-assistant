from datetime import date

from logger import AppLogger
from storage import db_session
from storage.postgres import Paper, User

logger = AppLogger(__name__).get_logger()
# from services.get_user_total_tokens import get_user_total_tokens


def get_or_create_user(db, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            last_query_date=date.today(),
            total_queries=0,
            remaining_tokens=1000,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def __get_all_papers_number(db) -> int:
    """回傳指定使用者已上傳的筆記數量"""
    # 確保使用者存在
    return db.query(Paper).count()


def get(user_id: str):
    with db_session() as db:
        user = get_or_create_user(db, user_id)
        logger.info(f"User {user_id} info retrieved: {user}")
        uploaded_papers = __get_all_papers_number(db)

        return {
            "user_id": user.id,
            "uploaded_papers": uploaded_papers,
            "last_query_date": user.last_query_date,
            "total_queries": user.total_queries,
            "remaining_tokens": user.remaining_tokens,
        }


def set_user_token_spend(user_id: str, remaining_tokens: int):
    with db_session() as db:
        user = get_or_create_user(db, user_id)
        user.remaining_tokens = user.remaining_tokens - remaining_tokens
        user.total_queries = user.total_queries + 1
        user.last_query_date = date.today()
