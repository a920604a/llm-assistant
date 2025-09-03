from datetime import date

from storage import db_session
from storage.postgres import User
from storage.storage_metrics import monitored_db


@monitored_db
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


@monitored_db
def set_user_token_spend(user_id: str, remaining_tokens: int):
    with db_session() as db:
        user = get_or_create_user(db, user_id)
        user.remaining_tokens = user.remaining_tokens - remaining_tokens
        user.total_queries = user.total_queries + 1
        user.last_query_date = date.today()
