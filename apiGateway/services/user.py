import requests
from config import settings


def get_user_data(user_id: str):
    # uploaded_papers: int
    # last_query_date: date
    # total_queries: int
    # remaining_tokens: int
    resp = requests.get(f"{settings.NOTE_API_URL}/api/v1/user/{user_id}", timeout=7)

    resp.raise_for_status()
    return resp.json()


def update_user_settings(user_id: str):
    pass
