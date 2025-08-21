from pydantic import BaseModel


class Query(BaseModel):
    text: str
    user_id: str
