from datetime import datetime
from typing import Optional

from storage import db_session
from storage.postgres import ChatHistory, User
from storage.storage_metrics import monitored_db


@monitored_db
def insert_chat_history(
    user_id: str,
    input_text: str,
    output_text: str,
    input_token: Optional[int] = None,
    output_token: Optional[int] = None,
    latency_ms: Optional[int] = None,
    model: Optional[str] = None,
):
    """
    將聊天紀錄存入 PostgreSQL
    """
    with db_session() as db:
        # 確保 user 存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            from storage.crud.user import get_or_create_user

            user = get_or_create_user(db, user_id)

        chat = ChatHistory(
            user_id=user.id,
            input=input_text,
            output=output_text,
            input_token=input_token,
            output_token=output_token,
            latency_ms=latency_ms,
            model=model,
            created_at=datetime.utcnow(),
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

    return chat
