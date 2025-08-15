from storage import db_session
from storage.postgres import User, Note
from datetime import date


def get_or_create_user(db, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            last_query_date=date.today(),
            total_queries=0,
            remaining_tokens=100,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_user_notes_number(user_id: str) -> int:
    """
    回傳指定使用者已上傳的筆記數量
    """

    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = get_or_create_user(db, user_id)
            return 0

        count = db.query(Note).filter(Note.user_id == user_id).count()
        return count


def __get_user_notes_number(db, user_id: str) -> int:
    """回傳指定使用者已上傳的筆記數量"""
    # 確保使用者存在
    get_or_create_user(db, user_id)
    return db.query(Note).filter(Note.user_id == user_id).count()


def get_info(user_id: str):
    with db_session() as db:
        user = get_or_create_user(db, user_id)
        uploaded_notes = __get_user_notes_number(db, user_id)

        return {
            "user_id": user.id,
            "uploaded_notes": uploaded_notes,
            "last_query_date": user.last_query_date,
            "total_queries": user.total_queries,
            "remaining_tokens": user.remaining_tokens,
        }
