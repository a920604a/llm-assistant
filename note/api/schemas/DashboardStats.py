from pydantic import BaseModel
from datetime import date


# 回傳格式定義
class DashboardStats(BaseModel):
    uploaded_notes: int
    last_query_date: date
    total_queries: int
    remaining_tokens: int