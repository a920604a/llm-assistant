from pydantic import BaseModel


class Query(BaseModel):
    text: str
    top_k: int = 5
    user_language: str = "Traditional Chinese"
