from datetime import datetime

from pydantic import BaseModel


class ChatMessage(BaseModel):
    # id: str
    role: str  # 'user' or 'bot'
    content: str
    timestamp: datetime
