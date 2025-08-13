from database import db_session
from database.postgres import UserData
from datetime import date


def create_user(db, user_id):
    user = UserData(
        user_id=user_id,
        uploaded_notes=0,
        last_query_date=date.today(),
        total_queries=0,
        remaining_tokens=100,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(user_id):
    with db_session() as db:
        user = db.query(UserData).filter(UserData.user_id == user_id).first()
        if not user:
            user = create_user(db, user_id)

        return {
            "user_id": user.user_id,
            "uploaded_notes": user.uploaded_notes,
            "last_query_date": user.last_query_date,
            "total_queries": user.total_queries,
            "remaining_tokens": user.remaining_tokens,
        }


def update_user(
    user_id,
    *,
    uploaded_notes=None,
    last_query_date=None,
    total_queries=None,
    remaining_tokens=None
):
    with db_session() as db:
        user = db.query(UserData).filter(UserData.user_id == user_id).first()
        if not user:
            # 可選擇自動建立新 user，或直接回傳 None / 錯誤
            user = create_user(db, user_id)

        # 更新欄位（有傳入的才更新）
        if uploaded_notes is not None:
            user.uploaded_notes = uploaded_notes
        if last_query_date is not None:
            user.last_query_date = last_query_date
        if total_queries is not None:
            user.total_queries = total_queries
        if remaining_tokens is not None:
            user.remaining_tokens = remaining_tokens

        db.commit()
        db.refresh(user)
        return user
