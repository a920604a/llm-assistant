from datetime import datetime
from typing import Optional

from logger import AppLogger
from storage import db_session
from storage.postgres import ChatHistory, User
from storage.set_user_token_spend import get_or_create_user
from storage.storage_metrics import monitored_db

logger = AppLogger(__name__).get_logger()


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
            user = get_or_create_user(db, user_id)
        logger.info(f"{datetime.now().astimezone()}")

        chat = ChatHistory(
            user_id=user.id,
            input=input_text,
            output=output_text,
            input_token=input_token,
            output_token=output_token,
            latency_ms=latency_ms,
            model=model,
            created_at=datetime.now().astimezone(),
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

    return chat


@monitored_db
def fetch_chat_history(
    user_id: str,
    limit: int = 50,  # 預設取最近 50 筆
):
    with db_session() as db:  # type: Session
        # 確保 user 存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        # 查詢最近 limit 筆聊天紀錄
        chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user.id)
            .order_by(ChatHistory.created_at.desc())  # 先按時間降序
            .limit(limit)
            .all()
        )

        # 前端通常希望 oldest -> newest，反轉列表
        chats.reverse()

        # 可以選擇返回 ORM 或轉成 dict
        return [
            {
                "id": str(chat.id),
                "input": chat.input,
                "output": chat.output,
                "timestamp": chat.created_at.isoformat(),
            }
            for chat in chats
        ]
