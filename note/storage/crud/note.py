from storage import db_session
from storage.postgres import User, Note
from datetime import date
from storage.crud.user import create_user


def update_note(
    user_id: str,
    uploaded_notes=None,
    last_query_date=None,
    total_queries=None,
    remaining_tokens=None,
):
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # 可選擇自動建立新 user，或直接回傳 None / 錯誤
            # user = create_user(db, user_id)
            return None

        # 更新欄位（有傳入的才更新）
        if uploaded_notes is not None:
            uploaded_notes = db.query(Note).filter(Note.user_id == user_id).count()
        if last_query_date is not None:
            user.last_query_date = last_query_date
        if total_queries is not None:
            user.total_queries = total_queries
        if remaining_tokens is not None:
            user.remaining_tokens = remaining_tokens

        db.commit()
        db.refresh(user)
        return user


def get_notes(user_id: str):
    with db_session() as db:
        notes = db.query(Note).filter(Note.user_id == user_id).all()
        return notes
