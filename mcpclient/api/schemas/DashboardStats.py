from datetime import date

from pydantic import BaseModel


# 回傳格式定義
class DashboardStats(BaseModel):
    uploaded_papers: int
    last_query_date: date
    total_queries: int
    remaining_tokens: int
