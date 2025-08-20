from pydantic import BaseModel


class UserQuery(BaseModel):
    query: str
    top_k: int = 5
    user_language: str = "Traditional Chinese"  # 假設使用者語言
